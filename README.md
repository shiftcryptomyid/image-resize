# SIZE24

## 1. Tujuan

SIZE24 adalah tool untuk mengolah image/sprite Ragnarok dengan dua fungsi utama:

1. **Build Collection & Item**

   * Berbasis source `.spr`.
   * Scan source SPR.
   * Extract image.
   * Membuat Collection dan Item.
   * Membuat atau memodifikasi file `.spr`.

2. **Free Recolor / Resize**

   * Berbasis source image.
   * Bisa digunakan untuk Single maupun Batch.
   * Recolor dan Resize dapat digunakan secara bebas.
   * AI Reconstruction akan ditambahkan kemudian.

---

# 2. Arsitektur Utama

```text
SIZE24
│
├── BUILD COLLECTION & ITEM
│   │
│   └── Source: SPR
│
│       Scan SPR
│          ↓
│       Extract Image
│          ↓
│       Collection
│          ↓
│       Item
│          ↓
│       Build / Modify SPR
│
│
└── FREE RECOLOR / RESIZE
    │
    └── Source: Image
        │
        ├── Single
        └── Batch
             ↓
          Recolor
             ↓
          Resize
             ↓
          AI Reconstruction
             ↓
          Output PNG / BMP
```

---

# 3. BUILD COLLECTION & ITEM

Fitur ini berorientasi pada **source SPR**.

## Input

Source berupa file:

```text
*.spr
```

Program akan melakukan scan terhadap source SPR dan mengambil image yang diperlukan.

## Collection

Hasil Collection menggunakan:

```text
100×100
```

Collection dapat menggunakan **CARD**.

CARD hanya digunakan untuk ukuran:

```text
100×100
```

Tujuan Collection adalah menghasilkan image yang lebih besar dan dapat digunakan untuk Collection.

AI Reconstruction nantinya dapat digunakan untuk membuat ulang Collection agar hasil visual dapat lebih bagus dan tidak harus identik dengan sprite asli.

## Item

Hasil Item menggunakan:

```text
24×24
```

Hasil Item nantinya digunakan untuk item dan item drop.

Output Item harus mendukung:

```text
BMP
```

## SPR

Build Collection & Item juga akan menangani pembuatan/modifikasi SPR.

Rencana proses:

```text
Source SPR
    ↓
Extract Image
    ↓
Collection 100×100
    ↓
Item 24×24
    ↓
Template Item SPR
    ↓
Replace Sprite #0
    ↓
Rename SPR
```

Jumlah Item SPR mengikuti jumlah source yang diproses.

---

# 4. FREE RECOLOR / RESIZE

Fitur ini berorientasi pada **source image**, bukan SPR.

Source dapat berupa image yang didukung oleh engine.

Terdapat dua mode:

```text
Single
Batch
```

## Single

Satu image diproses secara langsung.

Alur:

```text
Source Image
    ↓
Resize / Recolor
    ↓
AI (optional)
    ↓
Preview
    ↓
Save
```

## Batch

Banyak image diproses sekaligus.

Alur:

```text
Source Folder
    ↓
Scan Image
    ↓
Process setiap image
    ↓
Resize / Recolor
    ↓
AI (optional)
    ↓
Output Folder
```

Batch tidak menggunakan logic resize sendiri.

Batch akan menggunakan engine yang sama dengan Single.

---

# 5. Resize Engine

Resize Engine berada di:

```text
item_processor.py
```

Engine ini dibuat generik agar dapat digunakan oleh:

* Single Resize
* Batch Resize
* Build Collection
* Build Item
* Recolor
* AI pipeline

Engine menerima image dan pengaturan proses, kemudian menghasilkan:

```text
PIL Image
```

Engine tidak bertanggung jawab menentukan lokasi file output.

---

# 6. Ukuran Resize

Ukuran yang tersedia:

```text
24×24
60×60
100×100
Custom
```

Custom menggunakan:

```text
Width × Height
```

Contoh:

```text
80×64
```

Preset dan Custom diproses melalui:

```text
resolve_size()
```

---

# 7. Resize Method

Resize Method dipilih melalui UI.

Baseline yang telah ditetapkan:

```text
LANCZOS + ALPHA
```

Comparison resize sudah selesai dan digunakan sebagai dasar pemilihan metode.

AI Reconstruction akan menjadi pipeline terpisah dan tidak menggantikan standard resize engine.

---

# 8. Alpha & Background

Engine mendukung image dengan transparency.

Untuk standard resize:

```text
Alpha
```

dapat dipertahankan.

Background dapat dipilih dari UI.

CARD merupakan background khusus untuk:

```text
100×100
```

CARD tidak digunakan untuk:

```text
24×24
60×60
Custom selain 100×100
```

---

# 9. CARD Processor

CARD dibuat terpisah di:

```text
card_processor.py
```

Tujuannya agar desain CARD mudah diubah tanpa mengubah engine resize.

CARD digunakan untuk Collection:

```text
100×100
```

Karakteristik CARD yang sudah dibuat:

* rounded corner
* border
* shadow
* image ditempatkan di tengah
* image mengikuti batas ukuran yang ditentukan

---

# 10. Output Engine

Output ditangani oleh:

```text
output_processor.py
```

Format output utama:

```text
PNG
BMP
```

Output Processor menerima:

```text
PIL Image
```

kemudian menyimpannya ke format yang dipilih.

## PNG

Transparency dipertahankan apabila tersedia.

```text
RGBA
 ↓
PNG
 ↓
Alpha tetap
```

## BMP

BMP dipersiapkan sebagai RGB.

Jika source memiliki alpha:

```text
RGBA
 ↓
Composite Background
 ↓
RGB
 ↓
BMP
```

---

# 11. Pemisahan Engine dan UI

UI tidak boleh memiliki logic processing yang seharusnya berada di engine.

Struktur yang diinginkan:

```text
UI
│
├── spr_viewer.py
│
└── single_item.py
        │
        ▼
   Processing Engine
        │
        ├── item_processor.py
        ├── card_processor.py
        ├── output_processor.py
        └── ai_processor.py
```

UI bertugas mengatur:

* pilihan user
* preview
* dialog
* tombol
* input

Engine bertugas mengatur:

* image processing
* resize
* card
* AI
* output

---

# 12. AI Reconstruction

AI belum menjadi bagian aktif dari workflow saat ini.

Rencana:

```text
ai_processor.py
```

AI akan digunakan untuk:

* Reconstruction
* Upscaling
* Collection
* Recolor
* Resize

AI akan terhubung ke:

```text
ComfyUI
```

AI pipeline tetap terpisah dari standard resize.

```text
Standard Resize
        │
        └── item_processor.py

AI Reconstruction
        │
        └── ai_processor.py
                 │
                 └── ComfyUI
```

---

# 13. Rencana Pengembangan

Urutan pengembangan:

```text
1. Comparison Resize                 ✅
2. LANCZOS + ALPHA baseline          ✅
3. Generic item_processor.py         ✅
4. Single menggunakan engine        ✅
5. Preset 24×24 / 60×60 / 100×100   ✅
6. Custom Size                       ✅
7. Resize Method                     ✅
8. Background                        ✅
9. CARD 100×100                      ✅
10. Output PNG / BMP                 🔄
11. Single Save
12. Finalize Single Resize
13. Batch Image Resize
14. Build Collection & Item
15. SPR Builder
16. AI Reconstruction
17. ComfyUI Integration
18. Recolor
19. Batch Recolor / Resize
```

---

# 14. Prinsip Utama Project

### Engine harus reusable

Logic resize tidak ditulis ulang untuk setiap fitur.

```text
Single
Batch
Collection
Item
Recolor
AI
```

semuanya menggunakan engine yang sama jika membutuhkan fungsi tersebut.

### Image processing menghasilkan PIL Image

Processing engine tidak langsung menentukan lokasi penyimpanan.

```text
Image
 ↓
Processor
 ↓
PIL Image
 ↓
Output Processor
 ↓
PNG / BMP
```

### SPR logic dipisahkan dari Image logic

SPR Builder bertanggung jawab terhadap:

* scan SPR
* extract sprite
* replace sprite
* rename SPR
* template SPR
* struktur folder

Sedangkan Image Engine bertanggung jawab terhadap:

* resize
* recolor
* card
* AI
* output

---

# 15. Status Saat Ini

Fokus pengembangan saat ini:

```text
FREE RECOLOR / RESIZE
        ↓
      SINGLE
        ↓
      RESIZE
```

Yang sedang dikerjakan:

```text
Process
   ↓
Preview
   ↓
Output Format
   ├── PNG
   └── BMP
   ↓
Save
```

Setelah Single Resize stabil, baru dilanjutkan ke Batch dan kemudian Build Collection & Item.

