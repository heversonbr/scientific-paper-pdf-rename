#!/usr/bin/env python3
import fitz
import os
import sys
import platform
import pkg_resources
import signal
import string
import hashlib
import shutil
import re
import logging
from .helper import *

# Define logger / logger config
log_level = logging.INFO
logging.basicConfig(format='[%(asctime)s] - [%(levelname)s]- %(message)s' , level=log_level)
logger = logging.getLogger() 
set_helper_logger(log_level)

def keyboardInterruptHandler(signal, frame):
    logger.info('You pressed Ctrl+C! Leaving...'.format(signal))
    sys.exit(0)
         
def validate_arguments(arguments):
    
    if len(arguments) > 2:
        logger.error('Wrong number of arguments!')
        print_usage()
        sys.exit()

    if len(sys.argv) == 1:  
        logger.error("Missing arguments!")
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
            logger.error("Directory or file ["+ arguments[1] + "] path does not exist!")
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

def deprecating_get_page_text(current_page):
    '''
    this function is deprecating, keeping here as archive only.
    '''
    # first find python version
    #python_version = sys.version
    # Get the Python version as a string
    
    python_version = platform.python_version()
    tested_versions = ["3.11.6", "3.7.17", "3.8.18"]
    library_name = "PyMuPDF"
    library_version = pkg_resources.get_distribution(library_name).version

    if library_version == "1.18.14":        
        if python_version == "3.7.0":
            logger.debug('Python  version is: ' + python_version) 
            logger.debug('PyMuPDF version is: ' + library_version)
            blocks = current_page.getText('dict')['blocks']
        else: 
            logger.warn('Python  version is: ' + python_version) 
            logger.warn('PyMuPDF version is: ' + library_version)
            logger.error('Your Python version is not at the required level to work with PyMuPDF 1.18.14')
            logger.error('Please ensure that both meet the specified version requirements for this script to function properly.')
            sys.exit();
    elif library_version == "1.22.5":
        if python_version in tested_versions:
            blocks = current_page.get_text('dict')['blocks']
            logger.debug('Python  version is: ' + python_version) 
            logger.debug('PyMuPDF version is: ' + library_version)
        else:
            logger.warn('Python  version is: ' + python_version) 
            logger.warn('PyMuPDF version is: ' + library_version)
            logger.error('Your Python version is not at the required level to work with PyMuPDF 1.22.5')
            logger.error('Please ensure that both meet the specified version requirements for this script to function properly.')
            sys.exit();
    else: 
        logger.warn('Python  version is: ' + python_version) 
        logger.warn('PyMuPDF version is: ' + library_version)
        logger.error('Your Python version or PyMuPDF is not at the required level!')
        logger.error('Please ensure that both meet the specified version requirements for this script to function properly.')
        sys.exit()
    
    return blocks
    

def get_page_text(current_page):
    
    '''
        This fuunction is required for compatibility reasons. 
        there's a function get_text from PyMuPDF that changed its name from one version to the other. get_text or get_Text
        so this function just try to track the compatibility of that.
    '''
    # Get the current Python version and PyMuPDF version.
    python_version = platform.python_version()
    library_name = "PyMuPDF"
    library_version = pkg_resources.get_distribution(library_name).version

    # Define supported Python versions for PyMuPDF versions 1.22.5 and 1.26.0.
    tested_versions = ["3.11.6", "3.7.17", "3.8.18"]

    # Prepare a common version message.
    version_message = f"Python version: {python_version}, PyMuPDF version: {library_version}"

    if library_version == "1.18.14":
        if python_version == "3.7.0":
            logger.debug(version_message)
            blocks = current_page.getText('dict')['blocks']
        else:
            logger.warning(version_message)
            logger.error("Your Python version is not at the required level to work with PyMuPDF 1.18.14. "
                         "Please ensure that both meet the specified version requirements for this script to function properly.")
            sys.exit(1)
    elif library_version in ["1.22.5", "1.26.0", "1.22.0"]:
        if python_version in tested_versions:
            logger.debug(version_message)
            # Use get_text for these versions.
            blocks = current_page.get_text('dict')['blocks']
        else:
            logger.warning(version_message)
            logger.error(f"Your Python version is not at the required level to work with PyMuPDF {library_version}. "
                         "Please ensure that both meet the specified version requirements for this script to function properly.")
            sys.exit(1)
    else:
        logger.warning(version_message)
        logger.error("Your Python version or PyMuPDF is not at the required level! "
                     "Please ensure that both meet the specified version requirements for this script to function properly.")
        sys.exit(1)
    
    return blocks

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
    #blocks = page.get_text('dict')['blocks']
    blocks=get_page_text(page)
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
    #TODO: improve this above. to many 'for' in 'for'
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

def do_rename(fullpath_current_filename, fullpath_new_filename): 
    '''
    function do_rename: renames the file name given by the full path in 
                        'current_filename' to 'new_filename'
            receives: current_filename and 'new_filename
            returns: 
    ''' 
    logger.info('Renaming pdf file...')
    logger.info('Current file name: ' + fullpath_current_filename)
    logger.info('New file name: ' + fullpath_new_filename)

    if fullpath_current_filename == fullpath_new_filename: 
        logger.warning('Current filename and found title are already the same. Skipping...')
        return False
    
    logger.info("Renaming file...")
    
    try:
        os.rename(fullpath_current_filename, fullpath_new_filename)
    except:
        logger.error("An exception occurred. File not renamed!")
        return False
    finally:
        logger.debug("File renamed!")
        return True
    
def confirm_to_continue():
    
    logger.debug('Choose [c] to continue')
    logger.debug('Choose [s] to skip file')
    logger.debug('Choose [a] to abort')
    valid_choices = ['c', 's', 'a']
    choice = input('Choose [c] to continue, [s] to skip, or [a] to abort : \n')
    
    while(choice not in valid_choices):
        logger.warning('Answer not valid!')
        choice = input('Choose [c] to continue or [a] to abort : \n')
        
    if choice == 'c':
        return True
    
    if choice == 's':
        return False
            
    if choice == 'a':
        logger.info("aborting...")  
        sys.exit()
    
def select_loop_type():
    '''
    Function to allow user to select the loop mode, in the case of renaming all files in a directory. 
    User will be asked to choose between 'loop though all files and rename' and 'files one by one'  
    '''
    logger.info('Choose [1] : for renaming all pdf files in the directory')
    logger.info('Choose [2] : for one-by-one pdf file confirmation')
    valid_choices = ['1' , '2', 'q']
    choice = input('Choose [1], [2] or q [quit] : \n')
    
    while(choice not in valid_choices):
        logger.warning('Answer not valid!')
        choice = input('Choose [1], [2] or q [quit] : \n')
        
    if choice == '1':
        return '1'
            
    if choice == '2':
        return '2'
    
    if choice == 'q':
        logger.info("aborting...")
        sys.exit()
    
def move_file(fullpath_src_file, destination_dir, dest_file):
    
    if(not os.path.isdir(destination_dir)):
        os.mkdir(os.path.join(destination_dir))
    
    try: 
        #shutil.move(fullpath_src_file, destination_dir)
        shutil.move(fullpath_src_file, os.path.join(destination_dir, dest_file))
    except OSError as e:
        logger.exception(e.strerror)
        logger.warning('File ' + fullpath_src_file + ' was not moved to ' + destination_dir + '/auto_renamed_pdf' )
                
def search_candidate_title(src_dir, current_file):
    '''
    Generic function to search for one of the potential title candidates: based either on the metadata or on the font-size title
    '''
    
    counter = 0
    # look for title in the pdf file, returns 2 potential candidates (meta data in pdf and bigger-font sentence)
    meta_title, font_based_title = scan_title(src_dir + '/' + current_file)
    logger.debug('get_title returned:  [meta_title]: ' + meta_title + ' [found_title]: ' + font_based_title)   
    
    if len(font_based_title) > 0:
        # if found_title > 0: then font-based title was found. use font_based_title. 
        return font_based_title
    elif len(meta_title) > 0:
        # if meta_title > 0: then metadata title was found. user chooses between meta_title and mined title
        return meta_title
    else:
        logger.info('No potential Title was found for : ' + current_file)
        return None
               
def rename_files_in_dir(base_dir):
    '''
    For each pdf file in base_dir, 
    searches for a potential title in the pdf document (metadata and font-size)
    '''
    renamed_counter = 0
    total_counter = 0

    # file_fingerprints -> list of files (based on their hashes) used to avoid duplicated files. 
    #                      when a duplicated file is found it adds a 'dup' prefix to the file name
    file_fingerprints = []  
    full_path_base_dir = os.path.abspath(base_dir)

    if os.path.isdir(full_path_base_dir):
        list_of_files=[]
        for file in os.listdir(full_path_base_dir):
            if file.endswith('.pdf'):
                logger.debug('adding file to the list: ' + file)
                list_of_files.append(file)
        
        if len(list_of_files) < 1:
            logger.info('no pdf files found in the target directory')
            return renamed_counter, total_counter
        else: 
            logger.info(str(len(list_of_files)) + ' files found in the target directory!')
            loop_type=select_loop_type()
            
            for current_file in list_of_files:

                    total_counter+=1 
                    # use the hash of the file to avoir renaming files already renamed. 
                    # avoiding duplications. 
                    fingerprint = hash_file(full_path_base_dir + '/' + current_file)
                    logger.info('*' * 80)
                    logger.info('[Current file name] : ' + current_file)
                    logger.debug('[Current file hash] : ' + fingerprint) 
                    logger.debug('[loop_type] : ' + loop_type) 
                  
                    if loop_type == '2': 
                        answer = confirm_to_continue()
                        
                        if answer is False:
                            continue 
                    
                    if fingerprint not in file_fingerprints:
                        file_fingerprints.append(fingerprint)
                        found_title = search_candidate_title(full_path_base_dir, current_file)
                        if found_title is not None:
                            renamed = do_rename(full_path_base_dir + '/' + current_file, full_path_base_dir + '/' + found_title)
                            if renamed:
                                move_file(full_path_base_dir + '/' + found_title, full_path_base_dir + '/auto_renamed_pdf', found_title)
                                renamed_counter+=1
                    else: 
                        logger.warning('Another file with the same content (hash) was found in the source directory!')
                        logger.info('Skipping file: ' + current_file + ' adding prefix `duplicated_`to it')
                        os.rename(full_path_base_dir + '/' + current_file, full_path_base_dir + '/duplicated_' + current_file )
         

    else:
        logger.error('Directory does not exist!' )

    return renamed_counter, total_counter  
  
def rename_target_file(src_dir, filename):
    '''
    For received a pdf file in the command line 'src_dir / filename', 
    scans the file for a potential title in the pdf document (metadata and font-size)
    and call the method 'rename'
    '''

    fullpath_filename = src_dir + '/' + filename
    logger.debug('Searching file: ' + fullpath_filename)
    if os.path.isfile(fullpath_filename):
        if os.path.abspath(fullpath_filename).endswith('.pdf'):
            found_title = search_candidate_title(src_dir, filename)
            if found_title is not None:
                renamed = do_rename(fullpath_filename, src_dir + '/' + found_title)
                if renamed:
                    move_file(src_dir + '/' + found_title, src_dir + '/auto_renamed_pdf', found_title)
                    return True      
        else:
            logger.debug("File is not a pdf!")
            return False
    else:
            logger.error("File does not exist!")
            return False
      
import argparse
import os
import sys
import signal
import logging

logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Rename scientific papers based on their titles inside of PDF files."
    )
    parser.add_argument(
        "path",
        help="Path to a PDF file or a Directory containing PDF files."
    )

    args = parser.parse_args()

    path = os.path.abspath(args.path)
    base_dir = ''
    filename = ''

    if os.path.exists(path):
        if os.path.isdir(path):
            base_dir = path
        elif os.path.isfile(path) and path.endswith('.pdf'):
            base_dir = os.path.dirname(path)
            filename = os.path.basename(path)
        else:
            logger.error("Argument must be a PDF file or a Directory.")
            sys.exit(1)
    else:
        logger.error(f"Directory or file [{args.path}] path does not exist!")
        sys.exit(1)

    return base_dir, filename

def main():
        
    print_header()
    # validade arguments passed in the command line
    #base_dir, filename = validate_arguments(sys.argv)
    # use argparse instead of sys.argv
    base_dir, filename = parse_arguments()
    
    # set handler to capture the 'control+C' interruption from keyboard
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    
    
    # target path is either a (full path) directory or (full path) file name
    target_path = base_dir + '/' + filename
    logger.info('[Target Path]: ' + target_path)   
    
    rename_counter = 0 
    
    if os.path.isdir(target_path):
        # target is directory
        logger.debug('[base_dir]: ' + base_dir)
        rename_counter, total_counter = rename_files_in_dir(base_dir)
        logger.info('*' * 80)
        logger.info('Finished => Total files: ' + str(total_counter) + ' Renamed files: ' + str(rename_counter))

    else:
        # target is a file
        logger.debug('[base_dir]: ' + base_dir)
        logger.debug('[filename]: ' + filename)
        renamed = rename_target_file(base_dir, filename)
        logger.debug("Renamed? : " + str(renamed))
        if renamed: 
            rename_counter+=1 

        logger.info('*' * 80)
        logger.info('Finished => Renamed files : ' + str(rename_counter))

#if __name__ == "__main__":
#    main()