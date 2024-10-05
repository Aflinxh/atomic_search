from collections import defaultdict
import re
import difflib

def extract_atoms(target_words, search_space, min_atom_size):
    """
    Ekstraksi atom dari search_space untuk banyak target words berdasarkan min_atom_size setelah filtering dengan regex.
    Pisahkan calon atom berdasarkan simbol, kemudian seleksi sesuai kriteria min_atom_size.
    
    :param target_words: List dari kata target yang dicari.
    :param search_space: Ruang pencarian (misalnya string teks yang panjang).
    :param min_atom_size: Minimal ukuran atom yang dianggap valid.
    :return: Dictionary dari atom yang valid untuk setiap target word dan atom ambigu.
    """
    atoms = defaultdict(list)
    
    # Tentukan min_atom_size apakah dalam bentuk persentase atau jumlah huruf
    if isinstance(min_atom_size, str) and min_atom_size.endswith('%'):
        # Jika min_atom_size dalam bentuk persentase, ambil persentase minimum untuk setiap target word
        letter_thresholds = {target: len(target) * int(min_atom_size[:-1]) // 100 for target in target_words}
    else:
        # Jika min_atom_size berupa angka, gunakan angka tersebut untuk semua target
        letter_thresholds = {target: int(min_atom_size) for target in target_words}

    # Gunakan regex untuk memisahkan calon atom berdasarkan simbol non-alfabet
    candidate_atoms = re.split(r'[^a-zA-Z]+', search_space)  # Pisahkan string berdasarkan non-huruf

    # Seleksi calon atom yang merupakan substring dari target words
    for candidate in candidate_atoms:
        if len(candidate) == 0:
            continue  # Lewati jika kosong

        # Lacak target words yang cocok dengan atom ini
        matching_targets = []

        for target in target_words:
            # Cek apakah panjang kandidat memenuhi threshold untuk target ini
            if len(candidate) >= letter_thresholds[target]:
                # Pastikan bahwa kandidat adalah substring dari target word
                if any(candidate in target[i:i + len(candidate)] for i in range(len(target))):
                    matching_targets.append(target)

        # Masukkan atom ke target word yang sesuai atau ke 'ambigous_word' jika cocok lebih dari satu
        if len(matching_targets) == 1:
            atoms[matching_targets[0]].append(candidate)
        elif len(matching_targets) > 1:
            atoms['ambigous_word'].append(candidate)

    return atoms

def form_molecules(atoms, target_word, molecule_similarity, used_ambig_atoms, debugging=False):
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

    # Menggabungkan atom reguler dan ambiguous word sejak awal
    combined_initial_atoms = list(enumerate(atoms[target_word])) + [('ambiguous', j, ambig_atom) for j, ambig_atom in enumerate(atoms['ambigous_word'])]

    i = 0
    while i < len(combined_initial_atoms):
        entry = combined_initial_atoms[i]
        
        if len(entry) == 2:  # Atom dari target_word
            idx, atom = entry
            if debugging:
                print(f"Atom: {atom}")
            # Skip atom jika sudah digunakan atau gagal
            if idx in used_atoms_global or atom in failed_atoms:
                i += 1
                if debugging:
                    print(f"Atom: {atom} sudah digunakan, skipping...")
                continue
        elif len(entry) == 3:  # Atom dari ambigous_word
            _, idx, atom = entry
            if debugging:
                print(f"Ambiguous Atom: {atom}")
            # Skip jika ambiguous atom sudah digunakan
            if atom in used_ambig_atoms:
                i += 1
                if debugging:
                    print(f"Ambiguous Atom: {atom} sudah digunakan, skipping...")
                continue

        # Lewati atom yang tidak sesuai dengan bagian awal target_word
        if not target_word.startswith(atom):
            i += 1
            continue

        used_atoms_local = set()  # Simpan atom yang digunakan dalam molekul ini
        current_molecule = atom
        used_atoms_local.add(idx)  # Tandai atom sebagai digunakan dalam molekul ini
        target_index = len(current_molecule)  # Posisi dalam target_word yang sudah dipenuhi

        if debugging:
            print(f"Atom awal: {atom}, Molekul saat ini: {current_molecule}")

        # Gabungkan atom-atom berikutnya
        while target_index < target_len:
            remaining_target = target_word[target_index:]  # Substring yang belum terpenuhi dari target_word

            # Temukan atom berikutnya yang bisa cocok dengan sisa target
            next_atom_idx = None
            next_atom = None
            # Gabungkan atom dari target_word dan ambigous_word untuk iterasi
            combined_atoms = list(enumerate(atoms[target_word])) + [('ambiguous', j, ambig_atom) for j, ambig_atom in enumerate(atoms['ambigous_word'])]

            for entry in combined_atoms:
                if len(entry) == 2:  # Atom dari target_word
                    j, next_candidate = entry
                    if j not in used_atoms_local and j not in used_atoms_global and remaining_target.startswith(next_candidate):
                        next_atom_idx = j
                        next_atom = next_candidate
                        break
                elif len(entry) == 3:  # Atom dari ambigous_word
                    _, j, next_candidate = entry
                    if next_candidate not in used_ambig_atoms and remaining_target.startswith(next_candidate):
                        next_atom_idx = f"ambiguous_{j}"
                        next_atom = next_candidate
                        # Tandai ambiguous atom ini agar tidak digunakan lagi di iterasi selanjutnya
                        used_ambig_atoms.add(next_candidate)

                        if debugging:
                            print(f"Ambiguous atom '{next_candidate}' digunakan untuk melengkapi molekul saat ini.")

                        break

            if next_atom is None:  # Tidak ada atom yang cocok untuk dilanjutkan
                if debugging:
                    print(f"Atom {atom} gagal membentuk molekul yang valid.")
                failed_atoms.add(atom)  # Tandai atom ini sebagai gagal membentuk molekul
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

def atomic_search(target_words, search_space, min_atom_size, molecule_similarity, debugging=False):
    """
    Fungsi utama untuk melakukan pencarian dengan ekstraksi atom dan pembentukan molekul.
    :param target_words: List dari kata target yang dicari.
    :param search_space: Ruang pencarian (misalnya string teks yang panjang).
    :param min_atom_size: Minimal ukuran atom untuk dianggap valid.
    :param molecule_similarity: Minimal kemiripan (%) untuk dianggap sebagai molekul.
    :return: Dictionary dari jumlah total molekul yang terbentuk untuk setiap target word.
    """
    # Tahap 1: Ekstraksi atom dari search_space
    atoms = extract_atoms(target_words, search_space, min_atom_size)

    if debugging:
        print(f"{atoms}\n")

    # Buat set untuk menyimpan ambiguous atoms yang sudah digunakan secara global
    used_ambig_atoms = set()

    # Tahap 2: Bentuk molekul dari atom-atom untuk setiap target word
    results = {}
    for target_word in target_words:
        result = form_molecules(atoms, target_word, molecule_similarity, used_ambig_atoms, debugging)
        results[target_word] = result

    return results