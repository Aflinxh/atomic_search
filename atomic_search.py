from collections import defaultdict
import re
import difflib

# Perubahan pada extract_atoms
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
        letter_thresholds = {target: len(target) * int(min_atom_size[:-1]) // 100 for target in target_words}
    else:
        letter_thresholds = {target: int(min_atom_size) for target in target_words}

    # Gunakan regex untuk memisahkan calon atom berdasarkan simbol non-alfabet
    candidate_atoms = re.split(r'[^a-zA-Z]+', search_space)

    # Seleksi calon atom yang merupakan substring dari target words
    for candidate in candidate_atoms:
        if len(candidate) == 0:
            continue

        # Lacak target words yang cocok dengan atom ini
        matching_targets = []

        for target in target_words:
            if len(candidate) >= letter_thresholds[target]:
                if any(candidate in target[i:i + len(candidate)] for i in range(len(target))):
                    matching_targets.append(target)

        # Buat atom dengan format objek
        atom_object = {
            'value': candidate,
            'used': False
        }

        # Masukkan atom ke target word yang sesuai atau ke 'ambigous_word' jika cocok lebih dari satu
        if len(matching_targets) == 1:
            atoms[matching_targets[0]].append(atom_object)
        elif len(matching_targets) > 1:
            atoms['ambiguous_word'].append(atom_object)

    return atoms

def form_molecules(atoms, target_word, molecule_similarity, debugging=False):
    count = 0
    target_len = len(target_word)

    # Periksa apakah molecule_similarity adalah persentase atau toleransi huruf yang hilang
    if molecule_similarity.endswith('%'):
        similarity_threshold = int(molecule_similarity[:-1])
        use_percent_similarity = True
    elif molecule_similarity.startswith('-'):
        tolerance = abs(int(molecule_similarity))
        required_len = target_len - tolerance
        use_percent_similarity = False
    else:
        raise ValueError("molecule_similarity harus dalam bentuk persentase ('70%') atau toleransi ('-2').")

    # Gabungkan atom reguler dan ambiguous word
    combined_initial_atoms = atoms[target_word] + atoms['ambiguous_word']

    for atom in combined_initial_atoms:
        if debugging:
            print(f"Atom: {atom['value']}")
        # Lewati atom yang tidak sesuai dengan bagian awal target_word
        if not target_word.startswith(atom['value']):
            if debugging:
                print(f"Atom: {atom['value']} tidak memenuhi kata awal {target_word}, skipping...")
            continue

        # Gunakan atom saat ini untuk membentuk molekul
        current_molecule = atom['value']
        used_atoms_local = [atom]  # Simpan atom-atom yang sudah digunakan dalam percobaan ini
        target_index = len(current_molecule)

        if debugging:
            print(f"Atom awal: {atom['value']}, Molekul saat ini: {current_molecule}")

        # Gabungkan atom-atom berikutnya
        while target_index < target_len:
            remaining_target = target_word[target_index:]
            next_atom = None

            # Iterasi melalui semua atom yang tersedia
            for next_candidate in combined_initial_atoms:
                if debugging:
                    print(f"Next Candidate: {next_candidate}")

                if next_candidate not in used_atoms_local and next_candidate['used'] is False and remaining_target.startswith(next_candidate['value']):
                    next_atom = next_candidate
                    break

            if next_atom is None:  # Tidak ada atom yang cocok untuk dilanjutkan
                if debugging:
                    print(f"Gagal menemukan atom berikutnya untuk melengkapi molekul dari {current_molecule}")
                break

            # Gabungkan atom ke dalam molekul
            current_molecule += next_atom['value']
            used_atoms_local.append(next_atom)
            target_index += len(next_atom['value'])

            if debugging:
                print(f"Gabungan atom: {next_atom['value']}, Molekul saat ini: {current_molecule}")

        # Jika panjang molekul melebihi target_word, maka molekul tidak valid
        if len(current_molecule) > target_len:
            if debugging:
                print(f"Molekul {current_molecule} melebihi target_word, skip.")
            continue

        # Periksa kemiripan molekul dengan target_word
        if use_percent_similarity:
            similarity_score = difflib.SequenceMatcher(None, current_molecule, target_word).ratio() * 100
            if debugging:
                print(f"Similarity Score: {similarity_score}% untuk molekul {current_molecule}")
            if similarity_score >= similarity_threshold:
                count += 1
                # Tandai semua atom yang digunakan sebagai `used` hanya jika molekul valid
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                if debugging:
                    print(f"Valid Molecule: {current_molecule}")
        else:
            if len(current_molecule) >= required_len:
                count += 1
                # Tandai semua atom yang digunakan sebagai `used` hanya jika molekul valid
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                if debugging:
                    print(f"Valid Molecule: {current_molecule}")

        if debugging:
            print(f"Total Molekul yang ditemukan sejauh ini: {count}\n")

    return count

# Fungsi utama tetap sama tetapi akan memanfaatkan atom berbentuk objek
def atomic_search(target_words, search_space, min_atom_size, molecule_similarity, debugging=False):
    atoms = extract_atoms(target_words, search_space, min_atom_size)

    results = {}
    for target_word in target_words:
        if debugging:
            print(f"{atoms}\n")
        result = form_molecules(atoms, target_word, molecule_similarity, debugging)
        results[target_word] = result

    if debugging:
        print(f"{atoms}\n")
        
    return results