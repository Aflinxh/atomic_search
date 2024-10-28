import difflib

def form_molecule(atoms, target_word, molecule_similarity, logs=False):
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
        raise ValueError("molecule_similarity must be a percentage ('90%') or a tolerance ('-2').")

    combined_initial_atoms = atoms.get(target_word, []) + atoms.get('ambiguous_word', [])

    if logs:
        print(f"\n* Target Word: {target_word}")

    for atom in combined_initial_atoms:
        if logs:
            print(f"Atom: {atom}")
        if not target_word.startswith(atom['value']):
            if logs:
                print(f"Atom: {atom} does not match the beginning of {target_word}, skipping...")
            continue

        current_molecule = atom['value']
        used_atoms_local = [atom]
        target_index = len(current_molecule)

        if logs:
            print(f"- Starting Atom: {atom}, Current Molecule: {current_molecule}")

        while target_index < target_len:
            remaining_target = target_word[target_index:]
            next_atom = None

            for next_candidate in combined_initial_atoms:
                if logs:
                    print(f"Next Candidate: {next_candidate}")

                if next_candidate['id'] not in [atom['id'] for atom in used_atoms_local] and next_candidate['used'] is False and remaining_target.startswith(next_candidate['value']):
                    next_atom = next_candidate
                    break

            if next_atom is None:
                if logs:
                    print(f"Failed to find the next atom to complete the molecule from {current_molecule}")
                break

            current_molecule += next_atom['value']
            used_atoms_local.append(next_atom)
            target_index += len(next_atom['value'])

            if logs:
                print(f"- Combined atom: {next_atom['value']}, Current Molecule: {current_molecule}")

        if len(current_molecule) > target_len:
            if logs:
                print(f"Molecule {current_molecule} exceeds target_word, skipping.")
            continue

        if use_percent_similarity:
            similarity_score = difflib.SequenceMatcher(None, current_molecule, target_word).ratio() * 100
            if logs:
                print(f"-- Similarity Score: {similarity_score}% for molecule {current_molecule}")
            if similarity_score >= similarity_threshold:
                count += 1
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                    used_atom['combined'] = target_word  # Track the target word only if the molecule is valid
                if logs:
                    print(f"-- Valid Molecule: {current_molecule}")
        else:
            if len(current_molecule) >= required_len:
                count += 1
                for used_atom in used_atoms_local:
                    used_atom['used'] = True
                    used_atom['combined'] = target_word  # Track the target word only if the molecule is valid
                if logs:
                    print(f"-- Valid Molecule: {current_molecule}")

        if logs:
            print(f"--- Total molecules found so far: {count}\n")

    return count