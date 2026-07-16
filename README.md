# Teknofest İKA Parkur Simülasyonu (Gazebo)

2026 Teknofest parkurunun Gazebo Classic 11 simülasyonu:

- **Renkli parkur:** kırmızı-beyaz bariyerler, turuncu koniler, rampalar, su geçişi
- **Renkli görev tabelaları:** 2–11 arası sayılar (siyah/beyaz), STOP ve görev-sonu
  tabelaları (kırmızı/beyaz). Sayılar geometrik kabartma olduğu için her mesafede net.
- **Hareketli kayar engel:** 7 m'lik portal çerçevede sabit hızla gidip gelen perde
  (hız ve limitler ayarlanabilir)
- Skid-steer rover modeli + teleop (eski kurulum, `launch/gazebo.launch.py`)

## Gereksinimler

- Ubuntu 22.04, Gazebo Classic 11 (`sudo apt install gazebo libgazebo-dev`)
- Plugin derlemek için: `cmake`, `g++`
- (Rover için) ROS 2 Humble + `gazebo_ros_pkgs`

## Hızlı başlangıç — sadece parkuru açmak

```bash
cd src/rover_parkur
./baslat.sh
```

Script, kayar engel plugin'ini gerekiyorsa kendisi derler ve doğru ortam
değişkenleriyle Gazebo'yu açar.

## Kayar engel ayarları

`worlds/parkur_yeni.world` içinde, `kayar_engel` modelinin plugin bölümü:

```xml
<hiz>0.2</hiz>   <!-- kayma hızı, m/s -->
<alt>-2.2</alt>  <!-- başlangıca göre alt limit, m -->
<ust>1.8</ust>   <!-- başlangıca göre üst limit, m -->
```

Değiştirdikten sonra Gazebo'yu yeniden açmak yeterli, derleme gerekmez.

## Dosya yapısı

```
src/rover_parkur/
├── baslat.sh                  # parkuru tek komutla açar
├── worlds/parkur_yeni.world   # renkli parkur + hareketli engel (YENİ)
├── worlds/parkur.world        # eski boş world
├── meshes/parkur_yeni/        # renkli OBJ+MTL mesh'leri (metre, Z-up)
├── plugins/kayar_engel/       # perdeyi hareket ettiren Gazebo plugin'i (C++)
├── urdf/                      # rover ve eski parkur URDF'leri
├── launch/gazebo.launch.py    # ROS 2 launch (rover'lı eski kurulum)
└── src/                       # teleop ve kontrolcü scriptleri
```

## Bilinen notlar

- Tabela sayıları tek yüzdedir; sürüş yönüne göre yerleştirilmişlerdir
  (2,3,7-10 bir yöne, 4-6 ve 11'ler ters yöne bakar).
- "1" ve "12" tabelaları kaynak CAD modelinde bulunmuyor.
- Ölçek 1:1 gerçek boyuttur (parkur ~49×42 m, tabela çapı 60 cm,
  portal 7.09×2.46 m).
