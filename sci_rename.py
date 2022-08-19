#!/usr/bin/env python3
import fitz
import os
import sys
import signal
import string
import hashlib
import shutil
import re
import logging

# Define logger
log_level = logging.INFO
# logger config
logging.basicConfig(format='[%(asctime)s] - [%(levelname)s]- %(message)s' , level=log_level)
logger = logging.getLogger()   


def keyboardInterruptHandler(signal, frame):
    logger.info('You pressed Ctrl+C! Leaving...'.format(signal))
    sys.exit(0)

def print_usage():
    logger.info('********************************************************')
    logger.info('USAGE:    python3 rename_sci_paper.py [DIRECTORY]')
    logger.info('          python3 rename_sci_paper.py [PDF_FILENAME]')
    logger.info('********************************************************')

def print_header():
    print('*******************************************************************************')
    print('*                          RENAME my SCIENTIFIC PAPERS                        *')
    print('*******************************************************************************')
    print('*******************************************************************************')
         
def validate_arguments(arguments):
    
    if len(arguments) > 2:
        logger.error('Wrong number of arguments!')
        print_usage()
        sys.exit()

    if len(arguments) == 2:
        logger.debug(arguments[1])
        target = os.path.abspath(arguments[1])
        base_dir = ''
        filename = ''
        logger.debug('target : ' + target)
        
        if os.path.exists(target): 
            if os.path.isdir(target): 
                base_dir = os.path.abspath(target)
            else: 
                if target.endswith('.pdf'):
                    base_dir = os.path.dirname(target)
                    filename = os.path.basename(target)
                else: 
                    logger.error('Argument is not a pdf file')
                    sys.exit()
        else:
            logger.error("Directory or file path does not exist!")
            sys.exit()
    
    if len(sys.argv) == 1:  
        logger.error("Missing argument!")
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
        logger.error(target_file + ' is not a file')
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
    
    logger.info('*******************************************************************************')
    logger.info('Searching title for file : ' + full_file_name)
    if page_num is None:
        page_num = 0

    doc = fitz.open(full_file_name)
    meta_title = doc.metadata['title'].strip()
    
    # Check document's metadata for a potential title
    if len(meta_title) > 5:
        logger.debug('Document metadata title: ' + meta_title)
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
        #logger.debug('t_font_size: ' + str(t_font_size) + ' t_text: ' + t_text + ' t_text_len: ' + str(t_text_len))
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

    logger.debug('Parsed Found title: ' + parsed_found_title)
    logger.debug('--------------------------------------------------------')

    return(meta_title, parsed_found_title)

def do_rename(current_filename, new_filename, confirm_before=True): 
    '''
    function do_rename: renames the file name given by the full path in 
                        'current_filename' to 'new_filename'
            receives: current_filename and 'new_filename
            returns: 
    ''' 
    logger.info('Renaming pdf file...')
    logger.info('Current file name: ' + current_filename)
    logger.info('New file name: ' + new_filename)

    if current_filename == new_filename: 
        logger.warning('Current_filename and new_filename are the same. Skipping...')
        return False, confirm_before
    
    if confirm_before == True:
        valid_response = ['y', 'n', 'a', 'q']
        response = input('Do you agree (y/n/a/q) ? \n')
        while(response not in valid_response):
            logger.info('Answer not valid! Choose (y [yes], n [no], a [all], q [quit])')
            response = input('Do you agree (y/n/a/q) ? \n')

    else:
        # if set 'a' (all) , all files must be renamed without confirmation. it will set 'keep_confirming' to false below
        response = 'a'
        
    # check the user selection ('y', 'n', 'a' or 'q') 
    if response == 'y':
        logger.info("Renaming file...")
        os.rename(current_filename, new_filename)
        renamed = True
        keep_confirming = True
        logger.info("Done. ")
        
    elif response == 'a':
        logger.debug("Renaming files without confirmation...")
        os.rename(current_filename, new_filename)
        renamed = True
        keep_confirming = False
        logger.debug("Done. ")
        
    elif response == 'n':
        logger.warning('Skiping file...')
        logger.info('Keeping file name: \n' + current_filename)
        renamed = False
        keep_confirming = True
        
    elif response == 'q':
        logger.info('Quiting...')
        sys.exit()
    else:
        logger.error('Answer not valid !!!')
        logger.info('Keeping file as it is...')
        print_usage()
        renamed = False
        keep_confirming = True
        
    return renamed, keep_confirming
        
def choose_title(meta_title, found_title):
    '''
    Asks user to choose between two possible titles found
    '''
    
    if(meta_title == found_title):
        return found_title; 
        
    valid_choices = ['1' , '2', 'q']
    logger.info('** Found two candidates for title **')
    logger.info('[1] - [meta title] : ' + meta_title)
    logger.info('[2] - [mined title] : ' + found_title)
    
    choice = input('Choose [1], [2] or q [quit] : \n')
    while(choice not in valid_choices):
        logger.warning('Answer not valid!')
        choice = input('Choose [1], [2] or q [quit] : \n')
    
    if choice == '1':
        return meta_title
            
    if choice == '2':
        return found_title
    
    if choice == 'q':
        logger.info("leaving...")
        sys.exit()
    
def move_file(src_file, destination_dir):
    
    if(not os.path.isdir(destination_dir)):
        os.mkdir(os.path.join(destination_dir))
    
    try: 
        shutil.move(src_file, destination_dir)
    except OSError as e:
        logger.exception(e)
        logger.warning('File ' + src_file + ' was not moved to ' + destination_dir + '/auto_renamed')
           
def search_and_rename(src_dir, current_file, confirmation):
    '''
    generic function to search for one of the potential title candidates: metadata or font-size title
    '''
    
    counter = 0
    # look for title in the pdf file
    meta_title, found_title = scan_title(src_dir + '/' + current_file)
    logger.debug('get_title returned:  [meta_title]: ' + meta_title + ' [found_title]: ' + found_title )
        
    if len(meta_title) > 0:
        # if meta_title > 0: then metadata title was found. user chooses between meta_title and mined title     
        choosen_title = choose_title(meta_title, found_title)
    else:
        choosen_title = found_title       
 
    renamed, ask_confirmation = do_rename(src_dir + '/' + current_file, src_dir + '/' + choosen_title , confirmation)
    move_file(src_dir + '/' + choosen_title, src_dir + '/auto_renamed')
        
    if renamed == True:
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
    # file_fingerprints -> list of files (based on their hashes) used to avoid duplicated files. 
    #                      when a duplicated file is found it adds a 'dup' prefix to the file name
    file_fingerprints = []  
    full_path_base_dir = os.path.abspath(base_dir)

    if os.path.isdir(full_path_base_dir):
            
        list_of_files = os.listdir(full_path_base_dir)

        for current_file in list_of_files:
            if current_file.endswith('.pdf'):
                total_counter+=1 
                fingerprint = hash_file(full_path_base_dir + '/' + current_file)
                logger.debug('[Current file name] : ' + current_file)
                logger.debug('[Current file hash] : ' + fingerprint) 
                 
                if fingerprint not in file_fingerprints:
                    file_fingerprints.append(fingerprint)
                    result, ask_confirmation = search_and_rename(full_path_base_dir, current_file, confirmation)
                    rename_counter = rename_counter + result 
                    confirmation = ask_confirmation
                                       
                else: 
                    logger.warning('Another file with the same content (hash) was found in the source directory!')
                    logger.info('Skipping file: ' + current_file + ' adding prefix `dup_`to it')
                    os.rename(full_path_base_dir + '/' + current_file, full_path_base_dir + '/dup_' + current_file )
                    #print('----------------------------------------------------------------')

    else:
        logger.error('Directory does not exist!' )

    return rename_counter, total_counter  
       
def rename_target_file(src_dir, filename):
    '''
    For received a pdf file in 'src_dir / filename', 
    scans the file for a potential title in the pdf document (metadata and font-size)
    and call the method 'rename'
    '''

    fullpath_filename = src_dir + '/' + filename
    logger.debug('searching file: ' + fullpath_filename)

    counter = 0
    if os.path.isfile(fullpath_filename):
        if os.path.abspath(fullpath_filename).endswith('.pdf'):
    
            result, ask_confirmation = search_and_rename(src_dir, filename, True)
            counter = counter + result
                
        else:
            logger.error("File is not a pdf!")
             
    else:
            logger.error("File does not exist!")
            
    return counter
      
def main():
    
    print_header()
    # validade arguments passed in the command line
    base_dir, filename = validate_arguments(sys.argv)
    
    # set handler to capture the 'control+C' interruption from keyboard
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    confirmation=True
    
    # target path is either a (full path) directory or (full path) file name
    target_path = base_dir + '/' + filename
    logger.info('[Target Path]: ' + target_path)   
    logger.debug('[base_dir]: ' + base_dir)
    logger.debug('[filename]: ' + filename)
       
    if os.path.isdir(target_path):
        rename_counter, total_counter = rename_files_in_dir(base_dir)
    else:
        rename_counter = rename_target_file(base_dir, filename)
        total_counter = 1

    logger.info('*******************************************************************************')
    logger.info('Finished!')
    logger.info('Total files: ' + str(total_counter) + ' Files renamed: ' + str(rename_counter))

if __name__ == "__main__":

    main()