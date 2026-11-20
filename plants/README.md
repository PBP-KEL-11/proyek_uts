# Plants API

Base URL: `/api/plants/`

Autentikasi memakai session login (sama seperti API notes). Endpoint baca katalog
bisa diakses tanpa login, sedangkan semua operasi tulis dan endpoint kebun wajib login.

## Katalog Plant

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/plants/` | List katalog tanaman | Tidak |
| POST | `/api/plants/` | Tambah tanaman ke katalog | Ya |
| GET | `/api/plants/<id>/` | Detail tanaman | Tidak |
| PUT/PATCH | `/api/plants/<id>/` | Update tanaman | Ya |
| DELETE | `/api/plants/<id>/` | Hapus tanaman | Ya |

Query parameter list:

- `q` — cari berdasarkan `common_name` atau `scientific_name`
- `watering` — filter kebutuhan air, contoh `average`
- `sunlight` — filter kebutuhan cahaya, contoh `full_sun`

Field: `id`, `species_id`, `common_name`, `scientific_name`, `thumbnail`,
`watering`, `watering_days`, `sunlight`.

## Kebun User (GardenPlant)

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| GET | `/api/plants/garden/` | List tanaman milik user | Ya |
| POST | `/api/plants/garden/` | Tambah tanaman ke kebun | Ya |
| GET | `/api/plants/garden/<id>/` | Detail tanaman di kebun | Ya |
| PUT/PATCH | `/api/plants/garden/<id>/` | Update tanaman di kebun | Ya |
| DELETE | `/api/plants/garden/<id>/` | Hapus tanaman dari kebun | Ya |

Query parameter list:

- `q` — cari berdasarkan `plant.common_name` atau `nickname`

Field: `id`, `plant`, `plant_detail`, `nickname`, `notes`, `last_watered`,
`added_at`, `next_watering`, `needs_water`.

Contoh tambah ke kebun:

```json
{
  "plant": 1,
  "nickname": "Basil dapur"
}
```

`plant_detail`, `next_watering`, dan `needs_water` bersifat read-only.
Tanaman yang sama tidak bisa ditambahkan dua kali oleh user yang sama.
