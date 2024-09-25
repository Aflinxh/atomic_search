import re
import difflib

def extract_atoms(target_word, search_space, min_atom_size):
    """
    Ekstraksi atom dari search_space berdasarkan min_atom_size setelah filtering dengan regex.
    Pisahkan calon atom berdasarkan simbol, kemudian seleksi sesuai kriteria min_atom_size.
    :param target_word: Kata target yang dicari.
    :param search_space: Ruang pencarian (misalnya string teks yang panjang).
    :param min_atom_size: Minimal ukuran atom yang dianggap valid.
    :return: Array dari atom yang valid.
    """
    atoms = []
    
    # Tentukan min_atom_size apakah dalam bentuk persentase atau jumlah huruf
    if isinstance(min_atom_size, str) and min_atom_size.endswith('%'):
        percent_threshold = int(min_atom_size[:-1])  # Mengambil angka persen
        letter_threshold = len(target_word) * percent_threshold // 100  # Menghitung huruf berdasarkan persentase
    else:
        letter_threshold = int(min_atom_size)  # Jika min_atom_size berupa angka, gunakan angka tersebut

    # Gunakan regex untuk memisahkan calon atom berdasarkan simbol non-alfabet
    candidate_atoms = re.split(r'[^a-zA-Z]+', search_space)  # Pisahkan string berdasarkan non-huruf
    
    # Seleksi calon atom yang merupakan substring dari target_word
    for candidate in candidate_atoms:
        if len(candidate) == 0:
            continue  # Lewati jika kosong

        # Cek apakah panjang kandidat memenuhi min_atom_size
        if len(candidate) >= letter_threshold:
            # Pastikan bahwa kandidat adalah substring dari target_word
            if any(candidate in target_word[i:i + len(candidate)] for i in range(len(target_word))):
                atoms.append(candidate)

    return atoms

def form_molecules(atoms, target_word, molecule_similarity, debugging=False):
    count = 0
    target_len = len(target_word)

    # Periksa apakah molecule_similarity adalah persentase atau toleransi huruf yang hilang
    if molecule_similarity.endswith('%'):
        similarity_threshold = int(molecule_similarity[:-1])  # Mengambil angka persen, misalnya 70 dari '70%'
        use_percent_similarity = True
    elif molecule_similarity.startswith('-'):
        tolerance = abs(int(molecule_similarity))  # Ubah '-2' menjadi angka positif 2
        required_len = target_len - tolerance  # Panjang minimal untuk molekul valid
        use_percent_similarity = False
    else:
        raise ValueError("molecule_similarity harus dalam bentuk persentase ('70%') atau toleransi ('-2').")

    used_atoms_global = set()  # Simpan atom yang sudah berhasil digunakan untuk molekul
    failed_atoms = set()  # Simpan atom yang pernah gagal membentuk molekul

    i = 0
    while i < len(atoms):
        # Skip atom jika kita sudah tahu bahwa atom ini gagal membentuk molekul sebelumnya
        if atoms[i] in failed_atoms:
            i += 1
            continue

        # Lewati atom yang tidak sesuai dengan bagian awal target_word
        if not target_word.startswith(atoms[i]):
            i += 1
            continue

        if i in used_atoms_global:
            i += 1
            continue

        used_atoms_local = set()  # Simpan atom yang digunakan dalam molekul ini
        current_molecule = atoms[i]
        used_atoms_local.add(i)  # Tandai atom sebagai digunakan dalam molekul ini
        target_index = len(current_molecule)  # Posisi dalam target_word yang sudah dipenuhi

        if debugging:
            print(f"Atom awal: {atoms[i]}, Molekul saat ini: {current_molecule}")

        # Gabungkan atom-atom berikutnya
        while target_index < target_len:
            remaining_target = target_word[target_index:]  # Substring yang belum terpenuhi dari target_word

            # Temukan atom berikutnya yang bisa cocok dengan sisa target
            next_atom_idx = None
            next_atom = None
            for j, atom in enumerate(atoms):
                if j not in used_atoms_local and j not in used_atoms_global and remaining_target.startswith(atom):
                    next_atom_idx = j
                    next_atom = atom
                    break

            if next_atom is None:  # Tidak ada atom yang cocok untuk dilanjutkan
                if debugging:
                    print(f"Atom {atoms[i]} gagal membentuk molekul yang valid.")
                failed_atoms.add(atoms[i])  # Tandai atom ini sebagai gagal membentuk molekul
                break

            # Gabungkan atom ke dalam molekul
            current_molecule += next_atom
            used_atoms_local.add(next_atom_idx)  # Tandai atom sebagai digunakan dalam molekul ini
            target_index += len(next_atom)

            if debugging:
                print(f"Gabungan atom: {next_atom}, Molekul saat ini: {current_molecule}")

        # Jika panjang molekul melebihi target_word, maka molekul tidak valid
        if len(current_molecule) > target_len:
            if debugging:
                print(f"Molekul {current_molecule} melebihi target_word, skip.")
            i += 1
            continue

        # Jika similarity dalam bentuk persentase
        if use_percent_similarity:
            similarity_score = difflib.SequenceMatcher(None, current_molecule, target_word).ratio() * 100
            if debugging:
                print(f"Similarity Score: {similarity_score}% untuk molekul {current_molecule}")
            if similarity_score >= similarity_threshold:
                count += 1
                used_atoms_global.update(used_atoms_local)  # Simpan atom yang berhasil digunakan
                if debugging:
                    print(f"Valid Molecule: {current_molecule}")
        else:
            # Jika panjang molekul memenuhi syarat toleransi, hitung sebagai molekul valid
            if len(current_molecule) >= required_len:
                count += 1
                used_atoms_global.update(used_atoms_local)  # Simpan atom yang berhasil digunakan
                if debugging:
                    print(f"Valid Molecule: {current_molecule}")

        if debugging:
            print(f"Total Molekul yang ditemukan sejauh ini: {count}\n")

        i += 1  # Lanjutkan ke atom berikutnya

    return count

def atomic_search(target_word, search_space, min_atom_size, molecule_similarity, debugging=False):
    """
    Fungsi utama untuk melakukan pencarian dengan ekstraksi atom dan pembentukan molekul.
    :param target_word: Kata target yang dicari.
    :param search_space: Ruang pencarian (misalnya string teks yang panjang).
    :param min_atom_size: Minimal ukuran atom untuk dianggap valid.
    :param molecule_similarity: Minimal kemiripan (%) untuk dianggap sebagai molekul.
    :return: Jumlah total molekul yang terbentuk.
    """
    # Tahap 1: Ekstraksi atom dari search_space
    atoms = extract_atoms(target_word, search_space, min_atom_size)

    if debugging:
        print(f"{atoms}\n")

    # Tahap 2: Bentuk molekul dari atom-atom
    result = form_molecules(atoms, target_word, molecule_similarity, debugging)

    return result