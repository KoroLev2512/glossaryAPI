"""
Нагрузочное тестирование REST и gRPC API глоссария с помощью Locust
"""
import random
import time
from locust import HttpUser, TaskSet, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import grpc
import sys
from pathlib import Path

# Добавляем путь к proto модулям
sys.path.insert(0, str(Path(__file__).parent / "proto"))

try:
    from proto import glossary_pb2, glossary_pb2_grpc
except ImportError:
    print("Warning: gRPC proto files not found. Run 'make generate-grpc' first.")
    glossary_pb2 = None
    glossary_pb2_grpc = None


class RestGlossaryUser(HttpUser):
    """
    Класс пользователя для тестирования REST API
    Имитирует поведение клиента, работающего с глоссарием через REST
    """
    wait_time = between(1, 3)  # Пауза между запросами 1-3 секунды
    
    # Список ключевых слов для тестирования
    test_keywords = [
        "API", "REST", "gRPC", "HTTP", "JSON", "XML", 
        "SOAP", "GraphQL", "WebSocket", "TCP", "UDP"
    ]
    
    def on_start(self):
        """Выполняется при старте каждого пользователя"""
        # Проверка работоспособности
        self.client.get("/health", name="Health check")
    
    @task(3)
    def get_term(self):
        """Получение термина по ключевому слову (легкий запрос)"""
        keyword = random.choice(self.test_keywords)
        self.client.get(f"/terms/{keyword}", name="Get term by keyword")
    
    @task(2)
    def list_terms(self):
        """Получение списка всех терминов (более тяжелый запрос)"""
        self.client.get("/terms/", name="List all terms")
    
    @task(1)
    def create_term(self):
        """Создание нового термина (средний запрос)"""
        keyword = f"TEST_{random.randint(1000, 9999)}"
        payload = {
            "keyword": keyword,
            "description": f"Test description for {keyword}",
            "source": "https://test.example.com"
        }
        self.client.post("/terms/", json=payload, name="Create term")
    
    @task(1)
    def update_term(self):
        """Обновление термина (средний запрос)"""
        keyword = random.choice(self.test_keywords)
        payload = {
            "description": f"Updated description for {keyword}",
            "source": "https://updated.example.com"
        }
        self.client.put(f"/terms/{keyword}", json=payload, name="Update term")
    
    @task(1)
    def delete_term(self):
        """Удаление термина (легкий запрос)"""
        # Используем тестовый термин для удаления
        keyword = f"TEST_{random.randint(1000, 9999)}"
        self.client.delete(f"/terms/{keyword}", name="Delete term")


class GrpcGlossaryUser(TaskSet):
    """
    Класс пользователя для тестирования gRPC API
    Имитирует поведение клиента, работающего с глоссарием через gRPC
    """
    wait_time = between(1, 3)  # Пауза между запросами 1-3 секунды
    
    test_keywords = [
        "API", "REST", "gRPC", "HTTP", "JSON", "XML", 
        "SOAP", "GraphQL", "WebSocket", "TCP", "UDP"
    ]
    
    def on_start(self):
        """Выполняется при старте каждого пользователя"""
        # Создание gRPC канала
        self.channel = grpc.insecure_channel(self.user.host)
        self.stub = glossary_pb2_grpc.GlossaryServiceStub(self.channel)
    
    def on_stop(self):
        """Выполняется при остановке пользователя"""
        if hasattr(self, 'channel'):
            self.channel.close()
    
    @task(3)
    def get_term(self):
        """Получение термина по ключевому слову (легкий запрос)"""
        keyword = random.choice(self.test_keywords)
        request = glossary_pb2.GetTermRequest(keyword=keyword)
        start_time = time.time()
        try:
            response = self.stub.GetTerm(request, timeout=5)
            request_meta = {
                "request_type": "grpc",
                "name": "GetTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": None,
            }
            events.request.fire(**request_meta)
        except grpc.RpcError as e:
            request_meta = {
                "request_type": "grpc",
                "name": "GetTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": e,
            }
            events.request.fire(**request_meta)
    
    @task(2)
    def list_terms(self):
        """Получение списка всех терминов (более тяжелый запрос)"""
        request = glossary_pb2.ListTermsRequest(limit=100, offset=0)
        start_time = time.time()
        try:
            response = self.stub.ListTerms(request, timeout=5)
            request_meta = {
                "request_type": "grpc",
                "name": "ListTerms",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": None,
            }
            events.request.fire(**request_meta)
        except grpc.RpcError as e:
            request_meta = {
                "request_type": "grpc",
                "name": "ListTerms",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": e,
            }
            events.request.fire(**request_meta)
    
    @task(1)
    def create_term(self):
        """Создание нового термина (средний запрос)"""
        keyword = f"TEST_{random.randint(1000, 9999)}"
        request = glossary_pb2.CreateTermRequest(
            keyword=keyword,
            description=f"Test description for {keyword}",
            source="https://test.example.com"
        )
        start_time = time.time()
        try:
            response = self.stub.CreateTerm(request, timeout=5)
            request_meta = {
                "request_type": "grpc",
                "name": "CreateTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": None,
            }
            events.request.fire(**request_meta)
        except grpc.RpcError as e:
            request_meta = {
                "request_type": "grpc",
                "name": "CreateTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": e,
            }
            events.request.fire(**request_meta)
    
    @task(1)
    def update_term(self):
        """Обновление термина (средний запрос)"""
        keyword = random.choice(self.test_keywords)
        request = glossary_pb2.UpdateTermRequest(
            keyword=keyword,
            description=f"Updated description for {keyword}",
            source="https://updated.example.com"
        )
        start_time = time.time()
        try:
            response = self.stub.UpdateTerm(request, timeout=5)
            request_meta = {
                "request_type": "grpc",
                "name": "UpdateTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": None,
            }
            events.request.fire(**request_meta)
        except grpc.RpcError as e:
            request_meta = {
                "request_type": "grpc",
                "name": "UpdateTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": e,
            }
            events.request.fire(**request_meta)
    
    @task(1)
    def delete_term(self):
        """Удаление термина (легкий запрос)"""
        keyword = f"TEST_{random.randint(1000, 9999)}"
        request = glossary_pb2.DeleteTermRequest(keyword=keyword)
        start_time = time.time()
        try:
            response = self.stub.DeleteTerm(request, timeout=5)
            request_meta = {
                "request_type": "grpc",
                "name": "DeleteTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": None,
            }
            events.request.fire(**request_meta)
        except grpc.RpcError as e:
            request_meta = {
                "request_type": "grpc",
                "name": "DeleteTerm",
                "response_time": (time.time() - start_time) * 1000,
                "response_length": 0,
                "exception": e,
            }
            events.request.fire(**request_meta)


class GrpcUser(HttpUser):
    """
    Обертка для GrpcGlossaryUser, так как Locust требует HttpUser
    """
    tasks = [GrpcGlossaryUser]
    host = "localhost:50051"  # gRPC сервер
    wait_time = between(1, 3)
