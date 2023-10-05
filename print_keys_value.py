'''
Assume that a object named "my_obj" has three attributes
['att1', 'att2', 'att3']

Print out:
my_obj.att1
my_obj.att2
my_obj.att3
'''

# Print the values of all attributes
for attr in dir(my_obj):
    # Skip special attributes that start with '__'
    if not attr.startswith("__"):
        value = getattr(my_obj, attr)
        print('-'*70)
        print(f"{attr}: {value}")