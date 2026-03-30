import importlib.util
import inspect

spec=importlib.util.spec_from_file_location('trainer_mod','train_unified_sweet_spot.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cls=mod.UnifiedSweetSpotTrainer
attrs=dir(cls)
print('Has setup_data_loader:', hasattr(cls,'setup_data_loader'))
print('Attr count:', len(attrs))
print('First 30:', attrs[:30])
print('Last 30:', attrs[-30:])
print('Source tail:')
print('\n'.join(inspect.getsource(cls).splitlines()[-40:]))
