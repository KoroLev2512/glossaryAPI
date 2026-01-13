"""
Скрипт для генерации Python кода из .proto файлов
"""
import subprocess
from pathlib import Path

def generate_grpc_code():
    """Генерация Python кода из proto файлов"""
    proto_dir = Path("proto")
    output_dir = Path("proto")
    
    proto_file = proto_dir / "glossary.proto"
    
    if not proto_file.exists():
        print(f"Proto file not found: {proto_file}")
        return
    
    # Команда для генерации кода
    cmd = [
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file)
    ]
    
    print(f"Generating gRPC code from {proto_file}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Successfully generated gRPC code!")
        print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating gRPC code: {e}")
        print(f"Stderr: {e.stderr}")
        raise

if __name__ == "__main__":
    generate_grpc_code()
