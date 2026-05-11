# #Импортируем библиотеки
# from fastapi  import HTTPException, Query, APIRouter, Depends


# from typing import Literal
# import logging
# import json

# #Импортируем Pydantic-модели
# from schemas.schemas import *

# #Настраиваем логирование
# logging.basicConfig(level=logging.INFO, 
#                     filename="py_log.log", 
#                     filemode="a", 
#                     format="%(asctime)s %(levelname)s %(message)s", 
#                     encoding='utf-8')
# logger = logging.getLogger(__name__)

# #Создаём объект класса FastAPI
# legacy_router = APIRouter(prefix='/legacy', tags=['legacy'])

# def load_students() -> dict:
#     '''Читаем файл и возвращаем словарь словарей'''
#     #Пробуем прочитать файл
#     try:
#         with open('students.json', 'r') as f:
#             students = json.load(f)
#             return students
        
#     #Если файла не существует - создаём его
#     except FileNotFoundError:
#         #Создаём шаблон
#         template = {'1': {
#             'id': 1,
#             'name': 'Jon Snow',
#             'grade': 11,
#             'tariff': 'mini',
#         }}

#         with open('students.json', 'w') as f:
#             json.dump(template, f, indent=4)
        
#         return template

# def save_changes(students: dict) -> None:
#     '''Сохраняем изменения в файл'''
#     with open('students.json', 'w') as f:
#         json.dump(students, f, indent=4)
#     logger.info('Changes saved')

# def check_for_duplicates(student: dict) -> bool:
#     '''Проверяем на дубликаты'''
#     students = load_students()

#     any_duplicates = False
#     #Проходимя по каждому ученику в БД и сверяем их данные с данными нового ученика
#     for dicts in students.values():
#         if dicts['name'] == student['name'] and dicts['grade'] == student['grade'] and dicts['tariff'] == student['tariff']:
            
#             logger.warning(f'Duplicate-student creation rejected: id={dicts["id"]}')
#             any_duplicates = True
            
#     return any_duplicates

# @legacy_router.get('/', response_model=list[LegacyOut])
# def get_all_students(
#     #Для фильтрации
#     grade:   Literal['9', '10', '11'] | None = None,
#     tariff:  Literal['mini', 'standard', 'pro'] | None = None,
#     #Для сортировки
#     sort_by: Literal['id', 'name', 'grade', 'tariff'] = 'id',  #Задаём список параметров, по которому будем сортировать(по дефолту - сортируем по id)
#     order:   Literal['asc', 'desc'] = 'asc',       #Задаём сортировку в порядке возрастания/убывания 
#     #Для пагинации
#     offset: int = Query(default=0, ge=0),
#     limit:  int = Query(default=10, ge=1, le=100)
#     ):   
#     '''Отображаем всю базу данных'''
#     #Загружаем всех учеников из файла в словарь вида (id: {info})
#     students = load_students()
#     #Собираем список с информацией о всех студентах
#     students_list = list(students.values())

#     #Выкидываем из списка учеников с несовпадающим классом
#     if grade is not None:
#         students_list = [student for student in students_list if student['grade'] == int(grade)]
#     #Выкидываем из списка учеников с несовпадающим тарифом
#     if tariff is not None:
#         students_list = [student for student in students_list if student['tariff'] == tariff]
        
#     #Сортируем
#     students_list = sorted(
#         students_list, #Задаём список, по которому сортируем
#         key=lambda student: student[sort_by],  #Выбираем параметр для сортировки
#         reverse=(order=='desc'),      #Задаём сортировку по возрастанию/убыванию(выражение в скобках даёт True/False)
#         )

#     #Вырезаем необходимый кусок
#     students_list = students_list[offset: offset+limit]

#     return students_list

# @legacy_router.get('/{id}', response_model=LegacyOut)
# def get_student(id: int):
#     '''Отображаем конкретного ученика по id'''
#     students = load_students()
#     #Если в словаре есть студент с таким id - возвращаем его
#     if students.get(str(id)):
#         return students[str(id)]
#     else:
#         logger.warning(f'Student not found: id={id}')
#         raise HTTPException(status_code=404, detail='Student not found')

# @legacy_router.post('/', response_model=LegacyOut, status_code=201)
# def create_student(student: LegacyCreate):
#     '''Добавляем ученика'''
#     students = load_students()

#     #Проверяем на дублирование
#     new_student = student.model_dump()  #Заносим данные из модели в словрь
#     if check_for_duplicates(student=new_student):
#         raise HTTPException(status_code=409, detail='Duplicate-student creation rejected')

#     #Составляем список всех id, находим максимальный и увеличиваем его на 1
#     ids = [int(i) for i in students.keys()]
#     new_id = max(ids) + 1 
#     #Добавляем нового ученика в словарь
#     students[str(new_id)] = {
#         'id': new_id,
#         'name': student.name,
#         'grade': student.grade,
#         'tariff': student.tariff,
#     }
#     save_changes(students=students)

#     logger.info(f'Student was added: id={new_id}')
#     return students[str(new_id)]

# @legacy_router.delete('/{id}')
# def delete_student(id: int) -> dict:
#     students = load_students()

#     #Если не найден ученик с таким id - возвращаем ошибку
#     if students.get(str(id)) is None:
#         logger.warning(f'Student not found')
#         raise HTTPException(status_code=404, detail='Student not found')
    
#     #Удаляем студента
#     del students[str(id)]
    
#     logger.info(f'Student was deleted: id={id}')
#     save_changes(students)
#     return {'message': 'Student was deleted'}

# @legacy_router.put('/{id}', response_model=LegacyOut)
# def put_student_data(id: int, student: LegacyPut):
#     '''Обновляем всю информацию об ученике'''
#     students = load_students()

#     new_student = students.get(str(id))
#     if new_student is None:
#         logger.warning('Student not found')
#         raise HTTPException(status_code=404, detail='Student not found')
    
#     #Обновляем всю информацию
#     students[str(id)] = {
#         'id': id,
#         'name': student.name,
#         'grade': student.grade,
#        'tariff': student.tariff,
#     }
#     #Проверяем на дублирование
#     if check_for_duplicates(student=students[str(id)]):
#         raise HTTPException(status_code=409, detail='Duplicate-student creation rejected')
    
#     #Сохраняем изменения, если всё хорошо
#     save_changes(students=students)
#     logger.info(f'Student data was changed entirely: id={id}')
#     return students[str(id)]

# @legacy_router.patch('/{id}', response_model=LegacyOut)
# def patch_student_data(id: int, student: LegacyPatch):
#     '''Обновляем часть информации об ученике'''
#     students = load_students()
    
#     current_student = students.get(str(id))
#     if current_student is None:
#         logger.warning('Student not found')
#         raise HTTPException(status_code=404, detail='Student not found')
    
#     updated_student = current_student.copy()
#     #Сохраняем словарь с изменениями в новую переменную(аргумент функции выкидывает значения по умолчанию, оставляя только изменённое)
#     update_data = student.model_dump(exclude_unset=True)
#     updated_student.update(update_data)
    
#     #Проверяем на дублирование
#     if check_for_duplicates(student=updated_student):
#         raise HTTPException(status_code=409, detail='Duplicate-student creation rejected')
    
#     students[str(id)] = updated_student
#     #Сохраняем изменения, если всё хорошо
#     save_changes(students=students)
#     logger.info(f'Student data was changed partly: id={id}')
#     return students[str(id)]
