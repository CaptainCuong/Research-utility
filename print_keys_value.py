'''
Assume that a object named "cfg" has three attributes
['att1', 'att2', 'att3']

Print out:
cfg.att1
cfg.att2
cfg.att3
'''
for key in list(cfg.keys()):
    print('-'*20+f' {key} '+'-'*20)
    print(getattr(cfg, key))