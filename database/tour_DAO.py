from database.DB_connect import DBConnect
from model.tour import Tour

class TourDAO:

    @staticmethod
    def get_tour() -> dict[str, Tour] | None:
        """
        Restituisce tutti i tour
        :return: un dizionario di tutti i Tour
        """
        cnx = DBConnect.get_connection()
        result = {}
        if cnx is None:
            print("❌ Errore di connessione al database.")
            return None

        cursor = cnx.cursor(dictionary=True)
        query = """ SELECT * FROM tour """
        try:
            cursor.execute(query)
            for row in cursor:
                tour = Tour(
                    id=row["id"],
                    nome=row["nome"],
                    durata_giorni=row["durata_giorni"],
                    costo=row["costo"],
                    id_regione=row["id_regione"]
                )
                result[tour.id] = tour
        except Exception as e:
            print(f"Errore durante la query get_tour: {e}")
            result = None
        finally:
            cursor.close()
            cnx.close()

        return result

    @staticmethod
    def get_tour_attrazioni() -> list | None:
        """
        Restituisce tutte le relazioni
        :return: una lista di dizionari [{"id_tour": ..., "id_attrazione": ...}]
        """
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("❌ Errore di connessione al database.")
            return None

        cursor = cnx.cursor(dictionary=True)
        query = """ SELECT * FROM tour_attrazione """
        try:
            cursor.execute(query)
            for row in cursor:
                result.append({
                    "id_tour": row["id_tour"],
                    "id_attrazione": row["id_attrazione"]
                })
        except Exception as e:
            print(f"Errore durante la query get_tour_attrazioni: {e}")
            result = None
        finally:
            cursor.close()
            cnx.close()

        return result
