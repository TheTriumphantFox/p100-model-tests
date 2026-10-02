def recite(start_verse, end_verse):
    animals = [
        "fly",
        "spider",
        "bird",
        "cat",
        "dog",
        "goat",
        "cow",
        "horse",
    ]
    
    second_lines = {
        "fly": "I don't know why she swallowed the fly. Perhaps she'll die.",
        "spider": "It wriggled and jiggled and tickled inside her.",
        "bird": "How absurd to swallow a bird!",
        "cat": "Imagine that, to swallow a cat!",
        "dog": "What a hog, to swallow a dog!",
        "goat": "Just opened her throat and swallowed a goat!",
        "cow": "I don't know how she swallowed a cow!",
        "horse": "She's dead, of course!",
    }
    
    catch_lines = {
        "spider": "She swallowed the spider to catch the fly.",
        "bird": "She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.",
        "cat": "She swallowed the cat to catch the bird.",
        "dog": "She swallowed the dog to catch the cat.",
        "goat": "She swallowed the goat to catch the dog.",
        "cow": "She swallowed the cow to catch the goat.",
    }
    
    lines = []
    for i in range(start_verse, end_verse + 1):
        if i > start_verse:
            lines.append("")
            
        animal = animals[i - 1]
        lines.append(f"I know an old lady who swallowed a {animal}.")
        
        if animal == "horse":
            lines.append(second_lines["horse"])
        else:
            lines.append(second_lines[animal])
            
            # Add the cumulative catch lines in reverse order from current animal down to fly
            # The chain is: current -> previous -> ... -> fly
            # We need to generate lines for catching the previous animal, etc.
            # The "catch" line for animal X is "She swallowed X to catch Y" where Y is the previous animal.
            # But the line for spider is special because it includes the description.
            
            # Let's build the chain backwards from the current animal to the fly.
            # The lines are:
            # She swallowed [current] to catch [prev]
            # She swallowed [prev] to catch [prev_prev]
            # ...
            # She swallowed spider to catch fly.
            # I don't know why she swallowed the fly. Perhaps she'll die.
            
            # We iterate from the current animal index down to 1 (spider)
            # The catch line for animal at index j (0-indexed) catches animal at index j-1.
            # So for current index i-1, we need lines for indices i-1 down to 1.
            # The line for index j is "She swallowed {animals[j]} to catch {animals[j-1]}."
            # Except for spider (index 1), the line is "She swallowed the spider to catch the fly."
            # Wait, the spider line is "She swallowed the spider to catch the fly."
            # The bird line is "She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her."
            
            # Let's just use a predefined list of the full chain lines for each animal.
            # It's easier to hardcode the specific "catch" lines for each animal in the chain.
            
            for j in range(i - 1, 0, -1):
                current_animal = animals[j]
                prev_animal = animals[j - 1]
                
                if current_animal == "spider":
                    lines.append("She swallowed the spider to catch the fly.")
                elif current_animal == "bird":
                    lines.append("She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.")
                else:
                    lines.append(f"She swallowed the {current_animal} to catch the {prev_animal}.")
            
            lines.append("I don't know why she swallowed the fly. Perhaps she'll die.")
        
    return lines
