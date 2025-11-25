from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO
import copy

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self._tour_validi = []

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni = TourDAO.get_tour_attrazioni()

        if relazioni is None:
            return

        for row in relazioni:
            id_tour = row["id_tour"]
            id_attrazione = row["id_attrazione"]

            if id_tour in self.tour_map and id_attrazione in self.attrazioni_map:
                tour_obj = self.tour_map[id_tour]
                attr_obj = self.attrazioni_map[id_attrazione]

                if not hasattr(tour_obj, 'attrazioni'):
                    tour_obj.attrazioni = set()

                tour_obj.attrazioni.add(attr_obj)

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        self._tours_validi = [t for t in self.tour_map.values()
                              if t.id_regione == id_regione]

        self._ricorsione(start_index = 0,
                         pacchetto_parziale = [],
                         durata_corrente = 0,
                         costo_corrente = 0,
                         valore_corrente = 0,
                         attrazioni_usate = set(),
                         max_giorni = max_giorni,
                         max_budget = max_budget)

        return self._pacchetto_ottimo, self._costo_ottimo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set, max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
            self._costo_ottimo = costo_corrente

        for i in range(start_index, len(self._tours_validi)):
            tour = self._tours_validi[i]
            ids_attrazioni_tour = {a.id for a in tour.attrazioni}
            valore_culturale_tour = sum(a.valore_culturale for a in tour.attrazioni)

            if max_budget is not None and (costo_corrente + tour.costo) > max_budget:
                continue

            durata_tour = getattr(tour, 'durata_giorni', getattr(tour, 'durata', 0))
            if max_giorni is not None and (durata_corrente + durata_tour) > max_giorni:
                continue

            if len(attrazioni_usate.intersection(ids_attrazioni_tour)) > 0:
                continue

            pacchetto_parziale.append(tour)
            nuove_attrazioni_usate = attrazioni_usate.union(ids_attrazioni_tour)

            self._ricorsione(start_index=i + 1,
                             pacchetto_parziale=pacchetto_parziale,
                             durata_corrente=durata_corrente + durata_tour,
                             costo_corrente=costo_corrente + tour.costo,
                             valore_corrente=valore_corrente + valore_culturale_tour,
                             attrazioni_usate=nuove_attrazioni_usate,
                             max_giorni=max_giorni,
                             max_budget=max_budget)

            pacchetto_parziale.pop()