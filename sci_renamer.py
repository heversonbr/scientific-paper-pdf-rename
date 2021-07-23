#!/usr/bin/env python3
import fitz
import os
import sys
import signal
import string
import hashlib
import shutil
import re



def keyboardInterruptHandler(signal, frame):
    print('You pressed Ctrl+C! Leaving...'.format(signal))
    sys.exit(0)

def print_usage():
    print('--------------------------------------------------------------')
    print('USAGE: python3 rename_sci_paper.py [directory]')
    print('       python3 rename_sci_paper.py [pdf_filename.pdf]')
    print('--------------------------------------------------------------')
    
def validate_arguments(arguments):
    
    if len(arguments) > 2:
        print('Error: wrong number of arguments!')

    if len(arguments) == 2:
        #print(arguments[1])
        target = os.path.abspath(arguments[1])
        base_dir = ''
        filename = ''
        #print('target : ' + target)
        if os.path.exists(target): 
            if os.path.isdir(target): 
                base_dir = os.path.abspath(target)
            else: 
                if target.endswith('.pdf'):
                    base_dir = os.path.dirname(target)
                    filename = os.path.basename(target)
                else: 
                    print("Error: argument is not a pdf file")
                    sys.exit()
        else:
            print("Error: directory or file path does not exist!")
            sys.exit()
    
    if len(sys.argv) == 1:  
        print("Error: missing argument")
        print_usage()
        sys.exit()
        
    return base_dir, filename

def hash_file(target_file):
    
    blocksize = 65536
    hasher = hashlib.new('sha256')
    target_file = os.path.abspath(target_file)
    if os.path.isfile(target_file):
        
        with open(target_file, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                hasher.update(data)


        return hasher.hexdigest()
    else:
        print('error: ' + target_file + ' is not a file')
        sys.exit()
        
def parse_title(title, max_length=None):
    '''
    uses regex to parse the title/file-name candidate
    '''
    
    if max_length == None:
        max_length = 125
    
    if len(title) > max_length:
        title = title[:max_length]

    title = re.sub(r'[^a-zA-Z0-9]+', ' ' , title)
    title = title.strip()
    title=re.sub(r'\s', '_', title)
    title = string.capwords(title) + '.pdf'
    return title

def scan_title(full_file_name, page_num=None):
    '''
    scans the pdf file looking for a title, either based on the pdf metadata or 
    trying to figure out what is the sentence that has the larger font-size
    '''
    
    print('*******************************************************************************')
    print('Searching title for file : ' + full_file_name)
    if page_num is None:
        page_num = 0

    doc = fitz.open(full_file_name)
    meta_title = doc.metadata['title'].strip()
    
    # Check document's metadata for a potential title
    if len(meta_title) > 5:
        if verbose:  
            print('Document metadata title: ' + meta_title)
        meta_title = parse_title(meta_title)
    
    # Read first page and look for the setence with the largest font
    page = doc.load_page(page_num)
    size_text_tup_list =[]
    title=''
    # get paget text 
    blocks = page.getText('dict')['blocks']
    for blk in blocks:                              # iterate through text blocks
        if blk['type'] == 0:                        # only considers text blocks (type 0)
            for line in blk['lines']:               # iterate through text lines
                if line['dir'] == (1.0, 0.0) and line['wmode'] == 0:       # only considers horizontal lines: 
                                                    # check 'dir' argument (writing direction) in the Line dictionary 
                                                    # line['dir'] == (1.0, 0.0) write direction is horizontal left to right
                    for span in line['spans']:      # iterate through spans
                        size_text_tup = (span['size'], span['text'], span['origin'])
                        size_text_tup_list.append(size_text_tup)
                                                    # sort the list of tuples ('font_size','text_line') according to the 'font size' of a text line            
    # sort output 
    sorted_size_text_list=sorted(size_text_tup_list, key=lambda text_size: text_size[0], reverse=True)       
    
    larger_font = 0
    title_max_lines = 5
    
    for item in sorted_size_text_list:
        t_font_size = item[0]
        t_text = item[1]
        t_text_len = len(t_text)
        if verbose: 
            print('t_font_size: ' + str(t_font_size) + ' t_text: ' + t_text + ' t_text_len: ' + str(t_text_len))
        # consider only span text bigger than 2 , in order to avoid posible single characters 
        # with font size bigger than the Title being gotten as if they were the title. 
        # ex: in some papers the first letter of the paragraph is bigger than anything else, 
        # only getting the bigger font without considering the size of the text must generate titles that 
        # are as big as a single character. such as a.pdf, or b.pdf, thus only consider span at lines with more than 2 chars 
        if t_text_len > 2:
            
            if t_font_size > larger_font:           # compare the size of each item with the size of the larger font size 
                larger_font = t_font_size           # replace text if larger, append if it is the same 
                title = t_text.strip() + ' '
                title_max_lines-=1
            else:
                if t_font_size == larger_font:
                    title = title + t_text.strip() + ' '
                    title_max_lines-=1
        
        if title_max_lines < 1:
            break
                
                
    doc.close()
    parsed_found_title = parse_title(title)
    if verbose: 
        print('Parsed Found title: ' + parsed_found_title)
        print('--------------------------------------------------------')

    return(meta_title, parsed_found_title)

def do_rename(current_name, new_filename, confirmation=True): 
          
    print('*******************************************************************************')
    print('Renaming pdf file...')
    print('----------------------------------------------------------------')
    print('Current name: ' + current_name)
    print('----------------------------------------------------------------')
    print('New name: '  + new_filename)
    print('----------------------------------------------------------------')
    
    if current_name == new_filename: 
        print('Files already have the same name. Skipping...')
        return False, confirmation
    
    if confirmation == True:
        valid_response = ['y', 'n', 'a', 'q']
        response = input('Do you agree (y/n/a/q) ? \n')
        while(response not in valid_response):
            print('Answer not valid! Choose (y [yes], n [no], a [all], q [quit])')
            response = input('Do you agree (y/n/a/q) ? \n')

    else:
        response = 'a'
        
    if response == 'y':
        os.rename(current_name, new_filename)
        result = True
        ask_confimation = True
        print("Done. ")
        print('----------------------------------------------------------------')
    elif response == 'a':
        print("Renaming file...")
        os.rename(current_name, new_filename)
        result = True
        ask_confimation = False
        print("Done. ")
        print('----------------------------------------------------------------')
    elif response == 'n':
        print('Skiping file...')
        print('Keeping file name: \n' + current_name)
        result = False
        ask_confimation = True
        print('----------------------------------------------------------------')
    elif response == 'q':
        print('Quiting...')
        sys.exit()
    else:
        print('ERROR: Answer not valid !!!')
        print('Keeping file as it is...')
        print_usage()
        result = False
        ask_confimation = True
        #print('----------------------------------------------------------------')
        
    return result, ask_confimation
        
def choose_title(meta_title, found_title):
    '''
    Asks user to choose between two possible titles found
    '''
    
    if(meta_title == found_title):
        return found_title; 
        
    valid_choices = ['1' , '2', 'q']
    print('** Found two candidates for title **')
    print('[1] - [meta title] : ' + meta_title)
    print('[2] - [mined title] : ' + found_title)
    
    choice = input('Choose [1], [2] or q [quit] : \n')
    while(choice not in valid_choices):
        print('Answer not valid!')
        choice = input('Choose [1], [2] or q [quit] : \n')
    
    if choice == '1':
        return meta_title
            
    if choice == '2':
        return found_title
    
    if choice == 'q':
        print("leaving...")
        sys.exit()
    
def move_file(src_file, destination_dir):
    
    if(not os.path.isdir(destination_dir)):
        os.mkdir(os.path.join(destination_dir))
    
    try: 
        shutil.move(src_file, destination_dir)
    except OSError as e:
        print(e)
        print('Warning! : file ' + src_file + ' was not moved to ' + destination_dir + '/auto_renamed')
           
def search_and_rename(src_dir, current_file, confirmation):
    '''
    generic function to search for one of the potential title candidates: metadata or font-size title
    '''
    
    counter = 0
    
    # look for title in the pdf file
    meta_title, found_title = scan_title(src_dir + '/' + current_file)
    if verbose == True:
        print('get_title returned:  [meta_title]: ' + meta_title, ' [found_title]: ' + found_title )
        
    if len(meta_title) == 0: 
        # found no meta_title 
        result, ask_confirmation = do_rename(src_dir + '/' + current_file, src_dir + '/' + found_title, confirmation)
        move_file(src_dir + '/' + found_title, src_dir + '/auto_renamed')
        
        if result == True:
            counter = counter + 1
    else: 
        # found both meta_title and mined title     
        choosen_title = choose_title(meta_title, found_title)            
        result, ask_confirmation = do_rename(src_dir + '/' + current_file, src_dir + '/' + choosen_title , confirmation)
        move_file(src_dir + '/' + choosen_title, src_dir + '/auto_renamed')
        
        if result == True:
            counter = counter + 1

    return(counter, ask_confirmation)
                        
def rename_files_in_dir(base_dir):
    '''
    For each pdf file in base_dir, 
    searches for a potential title in the pdf document (metadata and font-size)
    '''
    rename_counter = 0
    total_counter = 0
    confirmation = True
    file_fingerprints = []
    full_path_base_dir = os.path.abspath(base_dir)

    if os.path.isdir(full_path_base_dir):
            
        list_of_files = os.listdir(full_path_base_dir)

        for current_file in list_of_files:
            if current_file.endswith('.pdf'):
                total_counter+=1 
                fingerprint = hash_file(full_path_base_dir + '/' + current_file)
                if verbose == True: 
                    print('[Current file name] : ' + current_file)
                    print('[Current file hash] : ' + fingerprint) 
                    
                if fingerprint not in file_fingerprints:
                    file_fingerprints.append(fingerprint)
                    result, ask_confirmation = search_and_rename(full_path_base_dir, current_file, confirmation)
                    rename_counter = rename_counter + result 
                    confirmation = ask_confirmation
                                       
                else: 
                    print('Another file with the same content (hash) was found in the source directory!')
                    print('Skipping file: ' + current_file + ' adding prefix `dup_`to it')
                    os.rename(full_path_base_dir + '/' + current_file, full_path_base_dir + '/dup_' + current_file )
                    print('----------------------------------------------------------------')

    else:
        print('Error: directory does not exist!' )
        print(src_dir)
   
    return rename_counter, total_counter  
       
def rename_target_file(src_dir, filename):
    '''
    For received a pdf file in 'src_dir / filename', 
    scans the file for a potential title in the pdf document (metadata and font-size)
    and call the method 'rename'
    '''

    fullpath_filename = src_dir + '/' + filename
    if verbose == True:
        print('searching file: ' + fullpath_filename)

    counter = 0
    if os.path.isfile(fullpath_filename):
        if os.path.abspath(fullpath_filename).endswith('.pdf'):
    
            result, ask_confirmation = search_and_rename(src_dir, filename, True)
            counter = counter + result
                
        else:
            print("Error: file is not a pdf!")
             
    else:
            print("Error: file does not exist!")
            print(fullpath_filename)
            
    return counter
      
def main():
    
    
    print('*******************************************************************************')
    print('*                          RENAME my SCIENTIFIC PAPERS                        *')
    print('*******************************************************************************')
    print('*******************************************************************************')
    # target path is either a (full path) directory or (full path) file name
    target_path = base_dir + '/' + filename
    print('[Target Path]: ')   
    print(target_path) 
    print('*******************************************************************************')
    if verbose == True:
        print('[base_dir]: ' + base_dir)
        print('[filename]: ' + filename)
        print('*******************************************************************************')
    
    if os.path.isdir(target_path):
        rename_counter, total_counter = rename_files_in_dir(base_dir)
    else:
        rename_counter = rename_target_file(base_dir, filename)
        total_counter = 1
    print('*******************************************************************************')
    print('Finished!  ')
    print('Total files: ' + str(total_counter) + ' , Files renamed: ' + str(rename_counter) )
    print('*******************************************************************************')
       
if __name__ == "__main__":
    
    base_dir, filename = validate_arguments(sys.argv)
    verbose=False
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    confirmation=True
    
    main()