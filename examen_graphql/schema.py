import strawberry
from typing import Optional


@strawberry.type
class Instructor:
    nombre: str


@strawberry.type
class Taller:
    nombre: str
    instructor: Instructor
    cupo: int
    activo: bool


@strawberry.input
class AgregarTallerInput:
    nombre: str
    instructor: str
    cupo: int
    activo: bool


_talleres = [
    Taller(
        nombre="Python para backend",
        instructor=Instructor(nombre="Ana López"),
        cupo=20,
        activo=True,
    ),
    Taller(
        nombre="Introducción a Docker",
        instructor=Instructor(nombre="Carlos Ruiz"),
        cupo=15,
        activo=False,
    ),
    Taller(
        nombre="Consultas con GraphQL",
        instructor=Instructor(nombre="Ana López"),
        cupo=25,
        activo=True,
    ),
]


@strawberry.type
class Query:
    @strawberry.field
    def talleres(self) -> list[Taller]:
        return _talleres

    @strawberry.field
    def taller(self, nombre: str) -> Optional[Taller]:
        for taller in _talleres:
            if taller.nombre == nombre:
                return taller
        return None

    @strawberry.field
    def talleres_activos(self) -> list[Taller]:
        return [taller for taller in _talleres if taller.activo]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_taller(self, taller: AgregarTallerInput) -> Taller:
        nuevo = Taller(
            nombre=taller.nombre,
            instructor=Instructor(nombre=taller.instructor),
            cupo=taller.cupo,
            activo=taller.activo,
        )
        _talleres.append(nuevo)
        return nuevo


schema = strawberry.Schema(query=Query, mutation=Mutation)