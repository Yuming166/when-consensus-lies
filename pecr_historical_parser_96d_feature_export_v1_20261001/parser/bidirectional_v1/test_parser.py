import sys
sys.path.insert(0,__import__('pathlib').Path(__file__).parent.as_posix())
from prepare_bidirectional import parse_num,norm_unit,parse_resp
assert parse_num('1,234.50')==1234.5
assert parse_num('') is None
assert norm_unit('percentage')=='%'
assert parse_resp({'parsed_json':{'answer_value':'12.5','unit':'percent','confidence':.9}})[0]['value']==12.5
assert parse_resp({'parsed_json':{'answer_value':'x','confidence':.9}})[1]=='answer_not_numeric'
assert parse_resp({'parsed_json':{'answer_value':'1','confidence':2}})[1]=='confidence_invalid'
print('synthetic parser tests passed')
