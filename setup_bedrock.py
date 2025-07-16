#!/usr/bin/env python3
"""
Amazon Bedrock快速配置脚本
帮助用户快速设置Amazon Bedrock Voice Conversation项目的环境
"""

import os
import sys
import subprocess
from pathlib import Path
import json


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("请安装Python 3.9或更高版本")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True


def install_dependencies():
    """安装依赖库"""
    print("\n📦 安装依赖库...")
    
    dependencies = [
        "boto3",
        "requests",
        "botocore"
    ]
    
    for dep in dependencies:
        try:
            print(f"正在安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 安装失败: {e}")
            return False
    
    return True


def setup_environment_variables():
    """设置环境变量"""
    print("\n🔧 设置环境变量...")
    
    # 获取用户输入
    print("请输入AWS配置信息:")
    
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("AWS Region (默认: us-east-1): ").strip() or "us-east-1"
    model_id = input("Model ID (默认: amazon.titan-text-express-v1): ").strip() or "amazon.titan-text-express-v1"
    
    # 设置环境变量
    os.environ["AWS_ACCESS_KEY_ID"] = access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    os.environ["AWS_DEFAULT_REGION"] = region
    os.environ["MODEL_ID"] = model_id
    
    print("✅ 环境变量设置完成")
    
    # 创建.env文件（可选）
    create_env_file = input("\n是否创建.env文件保存配置? (y/n): ").strip().lower()
    if create_env_file == 'y':
        env_content = f"""# Amazon Bedrock配置
AWS_ACCESS_KEY_ID={access_key}
AWS_SECRET_ACCESS_KEY={secret_key}
AWS_DEFAULT_REGION={region}
MODEL_ID={model_id}
"""
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ .env文件创建完成")
    
    return True


def check_project_path():
    """检查项目路径"""
    print("\n📁 检查项目路径...")
    
    project_path = "D:/amazon-bedrock-voice-conversation"
    
    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在: {project_path}")
        print("请确保Amazon Bedrock Voice Conversation项目已下载到该路径")
        return False
    
    # 检查关键文件
    required_files = ["app.py", "api_request_schema.py", "fine_tunning_data.py"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(project_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少关键文件: {', '.join(missing_files)}")
        return False
    
    print(f"✅ 项目路径检查通过: {project_path}")
    return True


def test_bedrock_connection():
    """测试Bedrock连接"""
    print("\n🚀 测试Bedrock连接...")
    
    try:
        import boto3
        
        # 创建Bedrock客户端
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
        
        # 测试连接
        model_id = os.getenv("MODEL_ID", "amazon.titan-text-express-v1")
        print(f"正在测试模型: {model_id}")
        
        # 简单的测试请求
        test_data = {
            "inputText": "Hello",
            "textGenerationConfig": {
                "maxTokenCount": 10,
                "temperature": 0.7,
                "topP": 0.9,
                "stopSequences": []
            }
        }
        
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(test_data)
        )
        
        print("✅ Bedrock连接测试成功")
        return True
        
    except ImportError:
        print("❌ boto3库未安装")
        return False
    except Exception as e:
        print(f"❌ Bedrock连接测试失败: {e}")
        return False


def create_test_script():
    """创建测试脚本"""
    print("\n📝 创建测试脚本...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Amazon Bedrock集成测试
\"\"\"

import os
import sys
from local_model_example import BedrockProjectAdapter

def test_bedrock():
    project_path = "D:/amazon-bedrock-voice-conversation"
    
    try:
        adapter = BedrockProjectAdapter(project_path)
        response = adapter.generate_text("请为成语猜多游戏出一道题目")
        print(f"✅ 测试成功: {response}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_bedrock()
"""
    
    with open("test_bedrock_simple.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 测试脚本创建完成: test_bedrock_simple.py")


def show_next_steps():
    """显示后续步骤"""
    print("\n" + "=" * 60)
    print("🎉 配置完成！")
    print("=" * 60)
    
    print("\n📋 后续步骤:")
    print("1. 运行测试脚本验证配置:")
    print("   python test_bedrock_simple.py")
    print("   python test_bedrock_integration.py")
    
    print("\n2. 启动成语猜多游戏:")
    print("   python idiom_guessing_gui.py")
    
    print("\n3. 在游戏设置中配置本地模型:")
    print("   - 模型路径: D:/amazon-bedrock-voice-conversation")
    print("   - API端点: 留空")
    
    print("\n4. 开始游戏并测试Amazon Bedrock集成")
    
    print("\n📞 如果遇到问题:")
    print("- 检查AWS凭证是否正确")
    print("- 确认模型在AWS账户中已启用")
    print("- 查看错误日志获取详细信息")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Amazon Bedrock Voice Conversation 快速配置")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return
    
    # 设置环境变量
    if not setup_environment_variables():
        print("❌ 环境变量设置失败")
        return
    
    # 检查项目路径
    if not check_project_path():
        print("❌ 项目路径检查失败")
        return
    
    # 测试Bedrock连接
    if not test_bedrock_connection():
        print("❌ Bedrock连接测试失败")
        return
    
    # 创建测试脚本
    create_test_script()
    
    # 显示后续步骤
    show_next_steps()


if __name__ == "__main__":
    main() 