


from .src.procedure_handler import ProcedureHandler as Handler

handler = Handler(sketch_files=['/dump/test_procedure.json'])
# handler.set_instruction(['/dump/test_procedure.json'])
handler.start()
