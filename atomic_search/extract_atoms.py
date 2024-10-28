import sys
import json
import csv
import os
from collections import defaultdict
import re

def extract_atoms(target_words, search_space, min_atom_size):
    atoms = defaultdict(list)

    for target in target_words:
        atoms[target] = []

    atom_id = 1
    
    if isinstance(min_atom_size, str) and min_atom_size.endswith('%'):
        letter_thresholds = {target: len(target) * int(min_atom_size[:-1]) // 100 for target in target_words}
    else:
        letter_thresholds = {target: int(min_atom_size) for target in target_words}

    candidate_atoms = re.split(r'[^a-zA-Z0-9]+', search_space)

    for candidate in candidate_atoms:
        if len(candidate) == 0:
            continue

        matching_targets = []

        for target in target_words:
            if len(candidate) >= letter_thresholds[target]:
                if any(candidate in target[i:i + len(candidate)] for i in range(len(target))):
                    matching_targets.append(target)

        if len(matching_targets) == 1:
            ref = matching_targets[0]
        elif len(matching_targets) > 1:
            ref = 'ambiguous_word'
        else:
            continue

        atom_object = {
            'id': atom_id,
            'value': candidate,
            'used': False,
            'ref': ref
        }

        atom_id += 1

        atoms[ref].append(atom_object)

    # Sorting atoms in descending order based on the length of 'value'
    for ref in atoms:
        atoms[ref] = sorted(atoms[ref], key=lambda atom: len(atom['value']), reverse=True)

    return atoms