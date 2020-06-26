# AAP14_Phyton-Abschlussprojekt_Chat-Server
FSST Abschlussprojekt Chat-Server

Bei diesem Projekt handelt es sich um einen Chat-Server mit zwei verschiedenen Chat-Client-Anwendungen (CLI und GUI). Der Chat-Server übernimmt hierbei den Großteil
der notwendigen Datenverarbeitung, wodurch der Chat-Client sich nur um das Senden, Empfangen und Darstellen der Nachrichten kümmern muss. Die vom Server erhaltenen
Nachrichten werden in einer Datenbank gespeichert und anschließend von diesem an alle anderen Chatteilnehmer weitergeleitet. Sowohl Server als auch Client benötigen
jeweils einen Thread fürd das Empfangen und einen für das Senden von Nachrichten, um gleichzeitig senden und empfangen zu können. Zur graphischen Darstellung stehen
clientseitig sowohl CLI als auch ein GUI-Design zur Verfügung. Die Kommunikation mit dem Server ist von der graphischen Darstellung unabhängig, es ist also möglich,
dass sich sowohl CLI- als auch GUI-Clients unterhalten können.

Klassen:
  Chat_Server: kümmert sich um das serverseitige Empfangen, Verarbeiten und Weiterleiten von Nachrichten
  Message: Datenbank, in welche am Server empfangene Nachrichten gespeichert werden
  Chat_Client: kümmmert sich um das clientseitige Empfangen, Darstellen und Senden von Nachrichten
  Chat_Window: Ergänzung des Chat-Clients; ermöglicht GUI
