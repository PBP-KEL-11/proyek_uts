import requests
from django.conf import settings
from django.core.cache import cache

BASE_URL = "https://perenual.com/api/v2"

class PerenualError(Exception):
    pass

def get_species_list(page=1, q="", **filters):
    params = {"key": settings.PERENUAL_API_KEY, "page": page}
    if q:
        params["q"] = q
    # filter opsional: watering, sunlight, indoor, edible, poisonous, cycle, dll
    params.update({k: v for k, v in filters.items() if v not in ("", None)})

    # cache biar hemat kuota request
    cache_key = "species_list:" + "&".join(f"{k}={v}" for k, v in sorted(params.items()) if k != "key")
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        resp = requests.get(f"{BASE_URL}/species-list", params=params, timeout=10)
    except requests.RequestException as e:
        raise PerenualError(f"Gagal konek ke Perenual: {e}")

    if resp.status_code == 429:
        raise PerenualError("Kena limit request. Coba lagi nanti.")
    if resp.status_code in (401, 403):
        raise PerenualError("API key ditolak.")
    if not resp.ok:
        raise PerenualError(f"Error dari API ({resp.status_code}).")

    data = resp.json()
    cache.set(cache_key, data, 60 * 60)  # simpan 1 jam
    return data

def get_species_detail(species_id):
    cache_key = f"species_detail:{species_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    resp = requests.get(
        f"{BASE_URL}/species/details/{species_id}",
        params={"key": settings.PERENUAL_API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    cache.set(cache_key, data, 60 * 60 * 24)  # detail jarang berubah, simpan 1 hari
    return data