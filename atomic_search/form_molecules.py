import difflib

def form_molecules(atoms, target_word, molecule_similarity, debugging=False):
    count = 0
    target_len = len(target_word)

    if molecule_similarity.endswith('%'):
        similarity_threshold = int(molecule_similarity[:-1])
        use_percent_similarity = True
    elif molecule_similarity.startswith('-'):
        tolerance = abs(int(molecule_similarity))
        required_len = target_len - tolerance
        use_percent_similarity = False
    else:
        raise ValueError("molecule_similarity harus dalam bentuk persentase ('70%') atau toleransi ('-2').")

    combined_initial_atoms = atoms[target_word] + atoms['ambiguous_word']

    for atom in combined_initial_atoms:
        if debugging:
            print(f"Atom: {atom}")
        if not target_word.startswith(atom['value']):
            if debugging:
                print(f"Atom: {atom} tidak memenuhi kata awal {target_word}, skipping...")
            continue

        current_molecule = atom['value']
        used_atoms_local = [atom]
        target_index = len(current_molecule)

        if debugging:
            print(f"- Atom awal: {atom}, Molekul saat ini: {current_molecule}")

        while target_index < target_len:
            remaining_target = target_word[target_index:]
            next_atom = None

            for next_candidate in combined_initial_atoms:
                if debugging:
                    print(f"Next Candidate: {next_candidate}")

                if next_candidate['id'] not in [atom['id'] for atom in used_atoms_local] and next_candidate['used'] is False and remaining_target.startswith(next_candidate['value']):
                    next_atom = next_candidate
                    break

            if next_atom is None:
                if debugging:
                    print(f"Gagal menemukan atom berikutnya untuk melengkapi molekul dari {current_molecule}")
                break

            current_molecule += next_atom['value']
            used_atoms_local.append(next_atom)
            target_index += len(next_atom['value'])

            if debugging:
                print(f"- Gabungan atom: {next_atom['value']}, Molekul saat ini: {current_molecule}")

        if len(current_molecule) > target_len:
            if debugging:
                print(f"Molekul {current_molecule} melebihi target_word, skip.")
            continue

        if use_percent_similarity:
            similarity_score = difflib.SequenceMatcher(None, current_molecule, target_word).ratio() * 100
            if debugging:
                print(f"-- Similarity Score: {similarity_score}% untuk molekul {current_molecule}")
            if similarity_score >= similarity_threshold:
                count += 1
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                if debugging:
                    print(f"-- Valid Molecule: {current_molecule}")
        else:
            if len(current_molecule) >= required_len:
                count += 1
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                if debugging:
                    print(f"-- Valid Molecule: {current_molecule}")

        if debugging:
            print(f"--- Total Molekul yang ditemukan sejauh ini: {count}\n")

    return count