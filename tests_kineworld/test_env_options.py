import ast
import copy
from pathlib import Path
from types import SimpleNamespace as NS
import unittest


class EnvTests(unittest.TestCase):
    def test_repeated_environment_creation_preserves_shared_options(self):
        source=ast.parse((Path(__file__).resolve().parents[1]/'dreamerv3/main.py').read_text())
        fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='make_env')
        calls=[]
        def ctor(task,**kwargs):calls.append(kwargs);return kwargs
        imports=NS(import_module=lambda name:NS(Dummy=ctor))
        scope=dict(importlib=imports,wrap_env=lambda env,config:env)
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'main.py','exec'),scope)
        config=NS(task='dummy_test',seed=42,env={'dummy':{'use_seed':True,'size':64}})
        original=copy.deepcopy(config.env)
        scope['make_env'](config,0,size=32)
        scope['make_env'](config,1)
        self.assertEqual(config.env,original)
        self.assertEqual(calls[0]['size'],32)
        self.assertEqual(calls[1]['size'],64)
        self.assertIn('seed',calls[0]);self.assertIn('seed',calls[1])
        self.assertNotEqual(calls[0]['seed'],calls[1]['seed'])

if __name__=='__main__':unittest.main()
