import requests

def obtener_info_bin(bin_numero):
    url = f"https://lookup.binlist.net/{bin_numero}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Ejemplo de uso
bin_numero = "52677734"
info_bin = obtener_info_bin(bin_numero)

if info_bin:
    print("Banco:", info_bin.get("bank", {}).get("name"))
    print("Tipo:", info_bin.get("type"))
    print("País:", info_bin.get("country", {}).get("name"))
else:
    print("No se encontró información para este BIN.")
