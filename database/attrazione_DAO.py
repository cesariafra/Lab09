from database.DB_connect import DBConnect
from model.attrazione import Attrazione

class AttrazioneDAO:

    @staticmethod
    def get_attrazioni() -> dict[str, Attrazione] | None:
        """
        Restituisce tutte le attrazioni
        :return: un dizionario di tutte le Attrazioni
        """
        cnx = DBConnect.get_connection()
        result = {}

        if cnx is None:
            print("❌ Errore di connessione al database.")
            return None

        cursor = cnx.cursor(dictionary=True)
        query = """ SELECT * FROM attrazione """
        try:
            cursor.execute(query)
            for row in cursor:
                attrazione = Attrazione(
                    id=row["id"],
                    nome=row["nome"],
                    valore_culturale=row["valore_culturale"]
                )
                result[attrazione.id] = attrazione
        except Exception as e:
            print(f"Errore durante la query get_attrazioni: {e}")
            result = None
        finally:
            cursor.close()
            cnx.close()

        return result
