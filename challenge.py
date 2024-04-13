import json
import csv

def process_XML(line, entry, entries):
    if "</ENT>" in line:
        # Remove items in entry with no values
        entry = {k: v for k, v in entry.items() if v != ''}

        # Save entries to encapsulating list
        entries.append(entry)
        entry = {
            'name': '',
            'organization': '',
            'street': '',
            'city': '',
            'county': '',
            'state': '',
            'zip': ''
        }
    
    # Iterate over lines, checking if key words found
    # Extract substring from each line and strip leading and following spaces
    if "NAME" in line:
        if line[6:-7].strip() != '':
            entry['name'] = line[6:-7].strip()

    if "COMPANY" in line:
        if line[9:-10].strip() != '':
            entry['organization'] = line[9:-10].strip()

    if "STREET" in line:
        if "_" in line:
            if line[10:-11].strip() != '':
                entry['street'] = entry['street'] + ' ' + line[10:-11].strip()
                entry['street'] = entry['street'].strip()
        else:
            if line[8:-9].strip() != '':
                entry['street'] = line[8:-9].strip()
        
    if "CITY" in line:
        if line[6:-7].strip() != '':
            entry['city'] = line[6:-7].strip()

    if "STATE" in line:
        if line[7:-8].strip() != '':
            entry['state'] = line[7:-8].strip()

    if "POSTAL_CODE" in line: 
        if line[13:-14].strip() != '':
            entry['zip'] = line[13:-14].strip()

    return entry, entries

def process_TSV(line, entry, entries):
    # Data organized by row
    # After the row is split into values, assign values to dictionary accordingly
    if (line[0] != '') or (line[1] != '') or (line[2] != ''):
        entry['name'] = (line[0] + ' ' + line[1] + ' ' + line[2]).strip()

    if line[3] != '':
        entry['organization'] = line[3]

    if line[4] != '':
        entry['street'] = line[4]

    if line[5] != '':
        entry['city'] = line[5]

    if line[6] != '':
        entry['state'] = line[6]

    if line[7] != '':
        entry['county'] = line[7]

    if (line[8] != '') or (line[9] != ''):
        entry['zip'] = line[8] + ' - ' + line[9]

        # Remove items in entry with no values
        entry = {k: v for k, v in entry.items() if v != ''}

        # Save entries to encapsulating list
        entries.append(entry)
        entry = {
            'name': '',
            'organization': '',
            'street': '',
            'city': '',
            'county': '',
            'state': '',
            'zip': ''
        }

    return entry, entries

def process_TXT(line, entry, entries, lines_read):
    # Data organized in batches of 3-4 lines, where the the extra line would include the county
    if lines_read == 1: 
        entry['name'] = line.strip()

    if lines_read == 2:
        entry['street'] = line.strip()

    if (lines_read == 3) and (('COUNTY' in line) or ('county' in line)):
        entry['county'] = line.strip()

    elif (lines_read == 3) or (lines_read == 4):
        line = line.split(',')
        entry['city'] = line[0].strip()
        entry['state'] = line[1].strip().split(' ')[0].strip()
        entry['zip'] = line[1].strip().split(' ')[1].strip()

        # Remove items in entry with no values
        entry = {k: v for k, v in entry.items() if v != ''}

        # Save entries to encapsulating list
        entries.append(entry)
        entry = {
            'name': '',
            'organization': '',
            'street': '',
            'city': '',
            'county': '',
            'state': '',
            'zip': ''
        }
        lines_read = 0

    return line, entry, entries, lines_read

if __name__ == "__main__":
    exit_status = 0
    
    while exit_status != 1:
        # Input prompt to user
        arg = input("Please enter '-f <filenames>' comma separated or '--help' for further options: ")

        # Usage and help
        if arg == "-help" or arg == "help" or arg == "-h" or arg == "" or arg == "--help" or ("-f" in arg and "." not in arg):
            print("\nUsage:")
            print("Enter '-q' or 'quit' \t\twhen you are finished.")
            print("Enter '-f <filenames>' \t\twhere <filenames> are the file names you wish to process, separated by commas.")
            print("Example: -f input1.xml, input2.tsv, input3.txt\n")

        elif arg == "-q" or arg == "quit":
            exit_status = 1
            break

        elif '-f' in arg:
            # Extract filenames fron input
            filenames = arg[3:]
            if ',' in filenames:
                filenames = filenames.split(',')
            else:
                filenames = [filenames]

            entries = []
            newEntry = False

            # Iterate and process each file
            for filename in filenames:
                filename = filename.strip()
                entry = {
                    'name': '',
                    'organization': '',
                    'street': '',
                    'city': '',
                    'county': '',
                    'state': '',
                    'zip': ''
                }

                try:
                    file = open(filename, 'r')
                except OSError:
                    print("Could not open/read file:", filename)
                    exit_status = 1
                    break

                if "xml" in filename:
                    for line in file:
                        line = line.strip()
                        entry, entries = process_XML(line, entry, entries)

                elif "tsv" in filename:
                    cr = csv.reader(file, delimiter='\t')
                    for line in cr:
                        if line[0] == 'first': 
                            continue
                        entry, entries = process_TSV(line, entry, entries)

                elif "txt" in filename:
                    lines_read = 0
                    for line in file:
                        line = line.strip()
                        if (len(line) == 0): 
                            continue

                        lines_read = lines_read + 1
                        line, entry, entries, lines_read = process_TXT(line, entry, entries, lines_read)

                else:
                    print('Error: Only files of type xml, tsv, or txt are accepted')
                    exit_status = 1
                    break
            break

    if exit_status == 0:
        if len(entries) < 1:
            print("There seems to be an error in the data file...")
        else:
            print(json.dumps(entries, indent=4))
            


            

        


