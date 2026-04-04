import os

def test():
    for n in range(10):
        en_names = {0: "0", 1: "01", 2: "02", 3: "03", 4: "04", 5: "05", 6: "06", 7: "07", 8: "08", 9: "09"}
        fname = f"en_num_{en_names[n]}.mp3"
        base_path = os.path.join(os.path.dirname(os.path.abspath('c:\\Users\\DELL 7540\\Desktop\\MusicalMe\\Mathic\\mathic_game.py')), '..', 'en_num', fname)
        base_path = os.path.abspath(base_path)
        print(f"EN {n}: {base_path} exists? {os.path.exists(base_path)}")

        fr_names = {0: "Zero", 1: "Un", 2: "Deux", 3: "Trois", 4: "Quatre", 5: "Cinq", 6: "Six", 7: "Sept", 8: "Huit", 9: "Neuf"}
        fname = f"{fr_names[n]}.mp3"
        base_path = os.path.join(os.path.dirname(os.path.abspath('c:\\Users\\DELL 7540\\Desktop\\MusicalMe\\Mathic\\mathic_game.py')), '..', 'fr_n', fname)
        base_path = os.path.abspath(base_path)
        print(f"FR {n}: {base_path} exists? {os.path.exists(base_path)}")

test()
