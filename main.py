"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
Curso: Programación 213023 - UNAD
Implementación académica en Python 3, sin bases de datos.
Los datos se mantienen en listas en memoria; los eventos y errores se escriben en logs.
"""
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from pathlib import Path


# ---------------------------------------------------------------------
# Configuración del registro de eventos y errores
# ---------------------------------------------------------------------
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("SoftwareFJ")


# ---------------------------------------------------------------------
# Excepciones personalizadas
# ---------------------------------------------------------------------
class SoftwareFJError(Exception):
    """Excepción base para los errores controlados del sistema."""


class ValidacionError(SoftwareFJError):
    """Se genera cuando un dato no cumple las reglas de validación."""


class NoEncontradoError(SoftwareFJError):
    """Se genera cuando no existe un cliente, servicio o reserva."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se genera cuando se intenta ejecutar una operación no permitida."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se genera cuando un servicio no está habilitado."""


# ---------------------------------------------------------------------
# Clase abstracta general: Entidad
# ---------------------------------------------------------------------
class Entidad(ABC):
    def __init__(self, identificador):
        if not isinstance(identificador, str) or not identificador.strip():
            raise ValidacionError("El identificador es obligatorio.")
        self._identificador = identificador.strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self):
        """Cada entidad concreta debe proporcionar su descripción."""


# ---------------------------------------------------------------------
# Cliente: encapsulación y validaciones
# ---------------------------------------------------------------------
class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionError("El nombre debe contener al menos 3 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValidacionError("El correo electrónico no tiene un formato válido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = str(valor).replace(" ", "").replace("-", "")
        if not limpio.isdigit() or len(limpio) < 7 or len(limpio) > 15:
            raise ValidacionError("El teléfono debe contener entre 7 y 15 dígitos.")
        self._telefono = limpio

    def describir(self):
        return f"Cliente {self.identificador}: {self.nombre} | {self.correo} | {self.telefono}"


# ---------------------------------------------------------------------
# Servicio abstracto y servicios especializados (herencia/polimorfismo)
# ---------------------------------------------------------------------
class Servicio(Entidad, ABC):
    IVA = 0.19

    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValidacionError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ValidacionError("La tarifa base debe ser un número positivo.")
        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = bool(disponible)

    @abstractmethod
    def calcular_costo(self, cantidad=1, impuesto=False, descuento=0):
        """Calcula el costo según el tipo concreto de servicio."""

    @abstractmethod
    def validar_parametros(self, cantidad):
        """Valida los parámetros específicos del servicio."""

    def describir(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.nombre} ({self.identificador}) - {estado}"

    def calcular_costo_detallado(self, cantidad=1, impuesto=False, descuento=0):
        """
        Variante de cálculo: admite cantidad, impuesto y descuento opcionales.
        En Python se implementa sobrecarga flexible mediante parámetros opcionales.
        """
        return self.calcular_costo(cantidad, impuesto, descuento)


class ReservaSala(Servicio):
    def __init__(self, identificador, nombre, tarifa_hora, capacidad):
        super().__init__(identificador, nombre, tarifa_hora)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ValidacionError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, cantidad):
        if not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise ValidacionError("La duración de la sala debe ser mayor que cero.")
        if cantidad > 24:
            raise ValidacionError("Una reserva de sala no puede superar 24 horas.")

    def calcular_costo(self, cantidad=1, impuesto=False, descuento=0):
        self.validar_parametros(cantidad)
        costo = self.tarifa_base * cantidad
        if not 0 <= descuento <= 100:
            raise ValidacionError("El descuento debe estar entre 0 y 100.")
        costo *= (1 - descuento / 100)
        if impuesto:
            costo *= (1 + self.IVA)
        return round(costo, 2)

    def describir(self):
        return f"{super().describir()} | Capacidad: {self.capacidad} personas"


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, tarifa_dia, unidades_disponibles):
        super().__init__(identificador, nombre, tarifa_dia)
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise ValidacionError("Las unidades disponibles deben ser un entero no negativo.")
        self.unidades_disponibles = unidades_disponibles

    def validar_parametros(self, cantidad):
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ValidacionError("Los días de alquiler deben ser un entero positivo.")
        if cantidad > 30:
            raise ValidacionError("El alquiler no puede superar 30 días.")

    def calcular_costo(self, cantidad=1, impuesto=False, descuento=0):
        self.validar_parametros(cantidad)
        if not 0 <= descuento <= 100:
            raise ValidacionError("El descuento debe estar entre 0 y 100.")
        costo = self.tarifa_base * cantidad * (1 - descuento / 100)
        if impuesto:
            costo *= (1 + self.IVA)
        return round(costo, 2)

    def describir(self):
        return f"{super().describir()} | Unidades disponibles: {self.unidades_disponibles}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, nombre, tarifa_hora, especialidad):
        super().__init__(identificador, nombre, tarifa_hora)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ValidacionError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, cantidad):
        if not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise ValidacionError("Las horas de asesoría deben ser mayores que cero.")
        if cantidad > 12:
            raise ValidacionError("Una asesoría no puede superar 12 horas por reserva.")

    def calcular_costo(self, cantidad=1, impuesto=False, descuento=0):
        self.validar_parametros(cantidad)
        if not 0 <= descuento <= 100:
            raise ValidacionError("El descuento debe estar entre 0 y 100.")
        costo = self.tarifa_base * cantidad * (1 - descuento / 100)
        if impuesto:
            costo *= (1 + self.IVA)
        return round(costo, 2)

    def describir(self):
        return f"{super().describir()} | Especialidad: {self.especialidad}"


# ---------------------------------------------------------------------
# Reserva: integra cliente, servicio, duración y estado
# ---------------------------------------------------------------------
class Reserva(Entidad):
    ESTADOS = {"PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA"}

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise ValidacionError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionError("La reserva requiere un objeto Servicio válido.")
        servicio.validar_parametros(duracion)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.fecha_creacion = datetime.now()

    def confirmar(self):
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError("El servicio seleccionado no está disponible.")
        self.estado = "CONFIRMADA"
        logger.info("Reserva %s confirmada para cliente %s", self.identificador, self.cliente.identificador)

    def cancelar(self):
        if self.estado not in {"PENDIENTE", "CONFIRMADA"}:
            raise OperacionNoPermitidaError("No se puede cancelar una reserva procesada o cancelada.")
        self.estado = "CANCELADA"
        logger.info("Reserva %s cancelada", self.identificador)

    def procesar(self, impuesto=False, descuento=0):
        if self.estado != "CONFIRMADA":
            raise OperacionNoPermitidaError("La reserva debe estar confirmada antes de procesarse.")
        try:
            total = self.servicio.calcular_costo_detallado(
                self.duracion, impuesto=impuesto, descuento=descuento
            )
        except ValidacionError as exc:
            logger.exception("Error al calcular el costo de la reserva %s", self.identificador)
            raise SoftwareFJError("No fue posible procesar el costo de la reserva.") from exc
        else:
            self.estado = "PROCESADA"
            logger.info("Reserva %s procesada. Total: %.2f", self.identificador, total)
            return total
        finally:
            logger.info("Finalizó el intento de procesamiento de reserva %s", self.identificador)

    def describir(self):
        return (f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
                f"Estado: {self.estado}")


# ---------------------------------------------------------------------
# Gestor: listas internas y operaciones centralizadas
# ---------------------------------------------------------------------
class GestorSistema:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ValidacionError("Solo se pueden registrar objetos Cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise OperacionNoPermitidaError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ValidacionError("El objeto suministrado no corresponde a un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise OperacionNoPermitidaError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.identificador)
        return servicio

    def crear_reserva(self, identificador, id_cliente, id_servicio, duracion):
        cliente = next((c for c in self.clientes if c.identificador == id_cliente), None)
        servicio = next((s for s in self.servicios if s.identificador == id_servicio), None)
        if cliente is None:
            raise NoEncontradoError(f"No existe el cliente {id_cliente}.")
        if servicio is None:
            raise NoEncontradoError(f"No existe el servicio {id_servicio}.")
        reserva = Reserva(identificador, cliente, servicio, duracion)
        self.reservas.append(reserva)
        logger.info("Reserva creada: %s", identificador)
        return reserva

    def buscar_reserva(self, identificador):
        reserva = next((r for r in self.reservas if r.identificador == identificador), None)
        if reserva is None:
            raise NoEncontradoError(f"No existe la reserva {identificador}.")
        return reserva

    def resumen(self):
        return {
            "clientes": len(self.clientes),
            "servicios": len(self.servicios),
            "reservas": len(self.reservas)
        }


# ---------------------------------------------------------------------
# Pruebas: más de 10 operaciones, casos correctos e incorrectos
# ---------------------------------------------------------------------
def ejecutar_demostracion():
    sistema = GestorSistema()
    print("\n========== SOFTWARE FJ: DEMOSTRACIÓN ==========")

    # 1. Registro válido de cliente
    try:
        c1 = sistema.registrar_cliente(Cliente("C001", "Laura Gómez", "laura@email.com", "3001234567"))
        print("1. Cliente registrado:", c1.describir())
    except SoftwareFJError as error:
        print("1. Error:", error)

    # 2. Registro de cliente inválido
    try:
        sistema.registrar_cliente(Cliente("C002", "Al", "correo-invalido", "123"))
    except SoftwareFJError as error:
        logger.exception("Prueba 2: registro inválido de cliente")
        print("2. Cliente inválido controlado:", error)

    # 3. Registro de segundo cliente válido
    try:
        c2 = sistema.registrar_cliente(Cliente("C003", "Carlos Pérez", "carlos@email.com", "3107654321"))
        print("3. Segundo cliente registrado:", c2.nombre)
    except SoftwareFJError as error:
        print("3. Error:", error)

    # 4. Creación de sala
    try:
        sala = sistema.registrar_servicio(ReservaSala("S001", "Sala de reuniones", 50000, 12))
        print("4. Servicio creado:", sala.describir())
    except SoftwareFJError as error:
        print("4. Error:", error)

    # 5. Creación de equipo
    try:
        equipo = sistema.registrar_servicio(AlquilerEquipo("S002", "Video beam", 80000, 4))
        print("5. Servicio creado:", equipo.describir())
    except SoftwareFJError as error:
        print("5. Error:", error)

    # 6. Creación de asesoría
    try:
        asesoria = sistema.registrar_servicio(
            AsesoriaEspecializada("S003", "Asesoría tecnológica", 100000, "Infraestructura TI")
        )
        print("6. Servicio creado:", asesoria.describir())
    except SoftwareFJError as error:
        print("6. Error:", error)

    # 7. Intento de servicio incorrecto
    try:
        sistema.registrar_servicio(ReservaSala("S004", "Sala inválida", -1000, 10))
    except SoftwareFJError as error:
        logger.exception("Prueba 7: creación incorrecta de servicio")
        print("7. Servicio inválido controlado:", error)

    # 8. Reserva correcta de sala
    try:
        r1 = sistema.crear_reserva("R001", "C001", "S001", 2)
        r1.confirmar()
        total = r1.procesar(impuesto=True)
        print(f"8. Reserva procesada: {r1.identificador} | Total: ${total:,.2f}")
    except SoftwareFJError as error:
        print("8. Error:", error)

    # 9. Reserva con cliente inexistente
    try:
        sistema.crear_reserva("R002", "C999", "S001", 1)
    except SoftwareFJError as error:
        logger.exception("Prueba 9: reserva con cliente inexistente")
        print("9. Reserva fallida controlada:", error)

    # 10. Reserva con duración inválida
    try:
        sistema.crear_reserva("R003", "C003", "S002", -2)
    except SoftwareFJError as error:
        logger.exception("Prueba 10: reserva con duración inválida")
        print("10. Duración inválida controlada:", error)

    # 11. Reserva de asesoría con descuento
    try:
        r2 = sistema.crear_reserva("R004", "C003", "S003", 3)
        r2.confirmar()
        total = r2.procesar(impuesto=True, descuento=10)
        print(f"11. Asesoría procesada: {r2.identificador} | Total: ${total:,.2f}")
    except SoftwareFJError as error:
        print("11. Error:", error)

    # 12. Cancelación de reserva
    try:
        r3 = sistema.crear_reserva("R005", "C001", "S002", 2)
        r3.cancelar()
        print("12. Reserva cancelada:", r3.estado)
    except SoftwareFJError as error:
        print("12. Error:", error)

    # 13. Intento de procesar reserva no confirmada y encadenamiento
    try:
        r4 = sistema.crear_reserva("R006", "C001", "S001", 1)
        r4.procesar()
    except SoftwareFJError as error:
        logger.exception("Prueba 13: procesamiento no permitido")
        print("13. Procesamiento no permitido controlado:", error)

    # 14. Método de costo con parámetros opcionales
    try:
        print("14. Costo con descuento (sin impuesto):",
              sala.calcular_costo(2, impuesto=False, descuento=5))
    except SoftwareFJError as error:
        print("14. Error:", error)

    # 15. Servicio no disponible
    try:
        equipo.disponible = False
        r5 = sistema.crear_reserva("R007", "C003", "S002", 1)
        r5.confirmar()
    except SoftwareFJError as error:
        logger.exception("Prueba 15: servicio no disponible")
        print("15. Servicio no disponible controlado:", error)

    print("\nResumen final:", sistema.resumen())
    print("Los eventos y errores se encuentran en logs/software_fj.log")
    print("========== FIN DE LA DEMOSTRACIÓN ==========\n")


if __name__ == "__main__":
    ejecutar_demostracion()
