import quick_config.settings as settings

def init(**kwargs):
    settings.VERBOSITY = kwargs['verbose'] if kwargs['verbose'] is not None else settings.VERBOSITY
    settings.LOG = kwargs['log'] if kwargs['log'] is not None else settings.LOG
    settings.APPLY = kwargs['apply'] if kwargs['apply'] is not None else settings.APPLY
    settings.PROMPT = kwargs['prompt'] if kwargs['prompt'] is not None else settings.PROMPT
