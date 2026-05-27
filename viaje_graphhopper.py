import urllib.request
import urllib.parse
import json
import sys

API_KEY         = "8c15fbde-103f-4cca-92d2-29774ea33aad"
CONSUMO_L_100KM = 10.0


def geocodificar(ciudad):
    query   = ciudad + ", Chile"
    encoded = urllib.parse.quote(query)
    url     = "https://nominatim.openstreetmap.org/search?q=" + encoded + "&format=json&limit=1"

    req = urllib.request.Request(url, headers={"User-Agent": "CalculadoraViajes/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            datos = json.loads(resp.read().decode())
        if not datos:
            return None
        return float(datos[0]["lat"]), float(datos[0]["lon"])
    except Exception as e:
        print("Error al geocodificar '" + ciudad + "': " + str(e))
        return None


def calcular_ruta(origen, destino):
    print("\nBuscando coordenadas de '" + origen + "'...")
    coords_origen = geocodificar(origen)
    if not coords_origen:
        print("No se encontro la ciudad: " + origen)
        return

    print("Buscando coordenadas de '" + destino + "'...")
    coords_destino = geocodificar(destino)
    if not coords_destino:
        print("No se encontro la ciudad: " + destino)
        return

    lat_o, lon_o = coords_origen
    lat_d, lon_d = coords_destino

    url = (
        "https://graphhopper.com/api/1/route"
        "?point=" + str(lat_o) + "," + str(lon_o) +
        "&point=" + str(lat_d) + "," + str(lon_d) +
        "&vehicle=car"
        "&locale=es"
        "&instructions=true"
        "&key=" + API_KEY
    )

    print("Consultando GraphHopper...\n")
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            datos = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode()
        print("Error HTTP " + str(e.code) + ": " + cuerpo)
        return
    except Exception as e:
        print("Error de red: " + str(e))
        return

    if "paths" not in datos or not datos["paths"]:
        print("GraphHopper no devolvio ninguna ruta.")
        return

    ruta = datos["paths"][0]

    distancia_km = ruta["distance"] / 1000.0
    duracion_s   = ruta["time"] / 1000.0
    horas        = int(duracion_s // 3600)
    minutos      = int((duracion_s % 3600) // 60)
    segundos     = duracion_s % 60
    combustible  = (distancia_km / 100.0) * CONSUMO_L_100KM

    linea = "-" * 50
    print(linea)
    print("VIAJE: " + origen.upper() + " -> " + destino.upper())
    print(linea)
    print("Distancia total  : " + format(distancia_km, ".2f") + " km")
    print("Duracion estimada: " + str(horas) + "h " + str(minutos) + "m " + format(segundos, ".2f") + "s")
    print("Combustible      : " + format(combustible, ".2f") + " litros")
    print("(consumo base    : " + format(CONSUMO_L_100KM, ".2f") + " L/100 km)")
    print(linea)

    instrucciones = ruta.get("instructions", [])
    if instrucciones:
        print("\nNARRATIVA DEL VIAJE\n")
        for i, paso in enumerate(instrucciones, 1):
            texto       = paso.get("text", "")
            dist_paso   = paso.get("distance", 0) / 1000.0
            tiempo_paso = paso.get("time", 0) / 1000.0
            t_min       = int(tiempo_paso // 60)
            t_seg       = tiempo_paso % 60

            print(str(i) + ". " + texto)
            if dist_paso > 0:
                print(
                    "   " +
                    format(dist_paso, ".2f") + " km  |  " +
                    str(t_min) + "m " + format(t_seg, ".2f") + "s"
                )
    print()


def main():
    print("=" * 50)
    print("  CALCULADORA DE VIAJES - GraphHopper")
    print("  Escribe 'q' para salir")
    print("=" * 50 + "\n")

    while True:
        try:
            origen = input("Ciudad de Origen  : ").strip()
            if origen.lower() == "q":
                break

            destino = input("Ciudad de Destino : ").strip()
            if destino.lower() == "q":
                break

            if not origen or not destino:
                print("Por favor ingresa ambas ciudades.\n")
                continue

            calcular_ruta(origen, destino)

        except KeyboardInterrupt:
            break

    print("\nHasta luego.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
