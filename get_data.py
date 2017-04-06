#!/usr/local/bin/python

import re
import sh
import sys
import os.path


if len(sys.argv) >= 3:
    class_name = sys.argv[2]
    file_name = sys.argv[1] + '/' + class_name + '.js'
else:
    print("Usage examples: \n./get_data.py src/menu Menu\n./get_data.py src/navbar NavBar")
    exit(1)

def get_column(s):
    return "{:0.2f}\t".format(s)

if not os.path.isfile(file_name):
    print(get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0) +
          get_column(0))
    exit(0)


def get_matches_from_file(regex, file_name):
    with open(file_name, 'r') as f:
        s = f.read()
        return re.findall(regex, s)


total_lines = 0
with open(file_name, 'r') as f:
    for line in f:
        if line != '\n':
            total_lines+=1

#####################
# Comment functions #
#####################
def find_substring(substring, string):
    indices = []
    index = -1  # Begin at -1 so index + 1 is 0
    while True:
        # Find next index of substring, by starting search from index + 1
        index = string.find(substring, index + 1)
        if index == -1:
            break  # All occurrences have been found
        indices.append(index)
    return len(indices)

def find_multiline_comments(string):
    multiline_count = 0
    comments = re.findall('(/\*([^*]|(\*+[^*/]))*\*+/)|(//.*)', string)
    for comment_tup in comments:
        for comment in comment_tup:
            block_comment_lines = find_substring("\n", comment)
            if block_comment_lines is not 0:
                multiline_count = multiline_count + find_substring("\n", comment) + 1
    return multiline_count

def get_number_of_comments(file_name):
    with open(file_name, 'r') as f:
        s = f.read()
        single_line_comments = len(re.findall('\/\/', s))
        multi_line_comments = find_multiline_comments(s)
        return single_line_comments + multi_line_comments
    
##########
# Number of methods
##########
number_of_methods = 0
with open(file_name, 'r') as f:
    s = f.read()
    matches = re.findall('\w*\([^(^)]*\)\s\{',s)
    number_of_methods = len(matches)

number_of_overridden_methods = 0
with open(file_name, 'r') as f:
    s = f.read()
    matches = re.findall('(componentWillMount|componentDidMount|componentWillReceiveProps|componentWillUpdate|componentDidUpdate|componentWillUnmount|constructor|render)\([^(^)]*\)\s\{',s)
    number_of_overridden_methods = len(matches)


############
# Get coupling
############
effCoupling = 0
with open(file_name, 'r') as f:
    s = f.read()
    matches = re.findall('import.*\.\/.*\;',s)
    effCoupling = len(matches)

import_regexp = "import.*" + class_name + "'*\;"
affCoupling = len(sh.grep("-r", import_regexp, "src", "index.android.js", "index.ios.js").splitlines())

############
# Get RFC
############

def get_rfc(file_name):
    with open(file_name, 'r') as f:
        s = f.read()
        method_lines = re.findall('\w*\([^(^)]*\)\s\{',s)
        methods = map(lambda x: re.findall('\w*\(',x)[0], method_lines)
        numbers = map(lambda x: sh.grep(" " + x,file_name,'-c'), methods)
        count = reduce(lambda x, y: int(x) + int(y), numbers)
        rfc = int(count)-len(method_lines)
        return rfc


##################
# Nesting functions #
##################
def update_max_nesting(curr, max):
    if (curr > max):
        return curr
    return max


def update_nesting(line, curr):
    opening_brace_regex = '{'
    closing_brace_regex = '}'
    opening = re.findall(opening_brace_regex, line)
    closing = re.findall(closing_brace_regex, line)
    return curr + len(opening) - len(closing)


def get_nesting_level(file):
    flist = open(file).readlines()
    method_regex = '( if| for| while| else).*\('
    parsing = False
    current_nesting_depth = 0
    max_nesting_depth = 0
    for line in flist:
        match = re.findall(method_regex, line);
        if match:
            parsing = True
        if parsing:
            current_nesting_depth = update_nesting(line, current_nesting_depth)
            max_nesting_depth = update_max_nesting(current_nesting_depth, max_nesting_depth)
            if (current_nesting_depth == 0):
                parsing = False
    return max_nesting_depth


########
# Get LCOM
########
def get_method_strings(file_name):
    flist = open(file_name).readlines()
    method_regex = '\w*\([^(^)]*\)\s\{'

    in_function = False
    current_nesting_depth = 0
    function_list = []
    start_row = 0
    for idx, line in enumerate(flist):
        match = re.findall(method_regex, line)
        if match:
            in_function = True
            start_row = idx
        if in_function:
            current_nesting_depth = update_nesting(line, current_nesting_depth)
            if (current_nesting_depth == 0):
                function_rows = flist[start_row:idx+1]
                function = "".join(function_rows)
                function_list.append(function)
                in_function = False
    return function_list


def is_attribute(x):
    if len(x) > 1 and x[-1] == ':':
        return True
    else:
        return False


def remake_attribute(x):
    return x[:-1]

def get_class_attributes(file_name):
    regex = re.compile('this.state (?:\s|.)*? };',re.MULTILINE)
    in_state = get_matches_from_file(regex,file_name)
    regex = re.compile('propTypes(?:\s|.)*?}',re.MULTILINE)
    in_props = get_matches_from_file(regex,file_name)
    if len(in_state) > 0:
        state_elements = in_state[0].split(' ')
    else:
        state_elements = []
    if len(in_props) > 0:
        props_elements = in_props[0].split(' ')
    else:
        props_elements = []
    attributes = map(remake_attribute,filter(is_attribute,state_elements)) + map(remake_attribute,filter(is_attribute,props_elements))
    return attributes


def get_sum_of_attributes_in_methods(file_name):
    method_list = get_method_strings(file_name)
    attribute_list = get_class_attributes(file_name)
    sum = 0
    for attribute in attribute_list:
        for method in method_list:
            if re.search(attribute, method):
                sum += 1
    return sum


def get_LCOM(file_name):
    a_sum = get_sum_of_attributes_in_methods(file_name)
    nr_attributes = len(get_class_attributes(file_name))
    if number_of_methods == 1:
        return 1
    return float((a_sum/nr_attributes)-number_of_methods)/float(1-number_of_methods)


########
# Get MFA
########
def get_mfa():
    inherited = ['componentWillMount','componentDidMount','componentWillReceiveProps','componentWillUpdate','componentDidUpdate','componentWillUnmount','constructor','render']
    return number_of_methods / (number_of_methods-number_of_overridden_methods+len(inherited))


#######
# Get remaining variables
#######
total_comments = get_number_of_comments(file_name)
rfc = get_rfc(file_name)
depth_of_inheritance = 1
lcom = get_LCOM(file_name)
mfa = get_mfa()
nesting_level = get_nesting_level(file_name)
subclasses = 0


#######
# Print result
#######

print(get_column(total_lines) +
      get_column(number_of_methods) +
      get_column(number_of_overridden_methods) +
      get_column(total_comments) +
      get_column(total_lines/number_of_methods) +
      get_column(total_comments/(total_comments+total_lines)) +
      get_column(rfc) +
      get_column(affCoupling) +
      get_column(effCoupling) +
      get_column(affCoupling + effCoupling) +
      get_column(depth_of_inheritance) +
      get_column(lcom) +
      get_column(mfa) +
      get_column(nesting_level) +
      get_column(number_of_overridden_methods/number_of_methods) +
      get_column(subclasses))

