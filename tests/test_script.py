from src.idea import generate_idea
from src.script import generate_script

idea = generate_idea()
print("IDEA:", idea)

script = generate_script(idea)
print("\nSCRIPT:\n", script)
