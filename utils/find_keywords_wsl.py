import os

file_dir = ['./path1', './path2', './path3']
keyword = ".*word_to_find.*"

for dir_ in file_dir:
	print('\n','-'*25,dir_,'-'*25,'\n')
	os.system(f'wsl -e sh -c "grep -worne {keyword} {dir_}"')
	print('\n','*-'*25,'\n')
os.system(f'wsl -e sh -c "grep -wone {keyword} *"')