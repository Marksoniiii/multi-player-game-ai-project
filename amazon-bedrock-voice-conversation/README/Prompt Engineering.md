# Amazon Bedrock Voice Conversation

## 项目概述
本项目提供了一个使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和其他支持的 AWS 服务与基础 AI 模型进行语音对话的示例实现。代码展示了如何构建一个支持自然来回语音对话的生成式 AI 应用程序。

## 项目结构
以下是项目的主要文件和文件夹结构及其说明：

### 根目录
- **`README.md`**: 本项目的说明文档，包含项目概述、运行步骤、配置微调等信息。
- **`CONTRIBUTING.md`**: 贡献指南，包含如何报告问题、提交拉取请求、发现可贡献的问题等内容。
- **`CODE_OF_CONDUCT.md`**: 行为准则，采用了 [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct)。
- **`LICENSE`**: 项目的许可证文件，本项目采用 MIT-0 许可证。
- **`requirements.txt`**: Python 依赖库列表，可使用 `pip install -r requirements.txt` 安装。
- **`sequence.txt`**: 记录了项目中涉及的提示词工程、RAG、上下文记忆、多模态、不同语言等方面的测试序列和输出示例。

### Python 脚本文件
- **`app.py`**: 项目的主应用程序文件，负责启动语音对话应用，包括用户语音输入处理、调用 Amazon Transcribe 进行语音转文本、调用 Amazon Bedrock 获取模型响应、使用 Amazon Polly 进行文本转语音等功能。
- **`api_request_schema.py`**: 定义了所有支持的基础模型的 API 请求模式，可根据需要修改每个模型的请求参数。
- **`fine_tunning_data.py`**: 包含大模型微调所需的数据，例如特定模型的系统提示和历史对话信息。

### 其他文件
- **`docs/amazon-bedrock-voice-conversation.png`**: 项目架构图，展示了语音对话流程中各个组件的交互方式。

## 运行步骤
### 前提条件
- Python 3.9 或更高版本。建议使用 [虚拟环境](https://docs.python.org/3.9/library/venv.html) 或 [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) 隔离项目环境。
- 一个具有足够权限使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/)、[Amazon Transcribe](https://aws.amazon.com/pm/transcribe) 和 [Amazon Polly](https://aws.amazon.com/polly/) 的 [IAM](https://aws.amazon.com/iam/) 用户。请确保计划使用的 Amazon Bedrock 基础模型在您的 AWS 账户中已启用，有关启用访问的详细信息，请参阅 [Model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)。

### 安装依赖库
运行以下命令安装 Python 依赖库：
```shell
pip install -r ./requirements.txt
```

### 配置 AWS 凭证和模型
设置 AWS 凭证和可选的基础模型（FM）作为环境变量：
```shell
export AWS_ACCESS_KEY_ID=<...>
export AWS_SECRET_ACCESS_KEY=<...>
export AWS_DEFAULT_REGION=<...> # 可选，默认为 us-east-1
export MODEL_ID=<...> # 可选，默认为 amazon.titan-text-express-v1
```

### 运行应用程序
最后，运行 Python 应用程序：
```shell
python ./app.py
```

## 进一步配置微调
### 模型 API 请求属性配置
`api_request_schema.py` 文件包含了所有支持模型的 FM API 请求模式。您可以根据需要更改每个模型的默认值，例如，对于 `amazon.titan-text-express-v1` 模型，您可以更改 `maxTokenCount`、`temperature` 或其他适用的属性。

### 全局配置映射
`app.py` 文件中创建了一个 `config` 字典，您可以更新该字典以进一步更改配置。例如，您可以将音频语音更改为 [Amazon Polly 支持的任何语音](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)，通过设置 `VoiceId` 为 `Joey`。

## 架构参考
为了提供最佳的语音对话用户体验，本解决方案在底层服务支持的情况下尽可能使用流式传输。具体来说，除了向 Amazon Bedrock 发送的 HTTP 请求外，每个步骤都使用流式传输。Amazon Bedrock 的响应也会流式传输回用户。

![架构图](./docs/amazon-bedrock-voice-conversation.png)

1. 用户语音音频以块的形式流式传输到 Amazon Transcribe 进行语音转文本转录。
2. Amazon Transcribe 在音频块到达时进行处理，逐步将其转录为文本。
3. 转录后的文本缓存在内存对象中，代表用户发送给 Amazon Bedrock 的完整消息。
4. 当用户说完后，将最终转录的文本消息作为 HTTP 请求发送到 Amazon Bedrock。
5. Amazon Bedrock 的文本响应流式传输回进行文本转语音转换。
6. 随着 Amazon Bedrock 响应的文本块到达，它们被提交给 Amazon Polly 合成语音音频。此过程使用流式传输。
7. Polly 语音音频块在到达时逐步在用户设备上播放。

## 安全与许可
### 安全问题通知
如果您发现本项目中存在潜在的安全问题，请通过 [漏洞报告页面](http://aws.amazon.com/security/vulnerability-reporting/) 通知 AWS/Amazon 安全团队。请**不要**创建公开的 GitHub 问题。

### 许可
本库采用 MIT-0 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 贡献指南
欢迎通过 GitHub 问题跟踪器报告错误或提出功能建议。在提交问题时，请检查现有的开放或最近关闭的问题，确保其他人尚未报告过相同的问题。请尽量提供尽可能多的信息，例如可重现的测试用例、使用的代码版本、与错误相关的任何修改以及环境或部署的任何异常情况。

有关如何提交拉取请求的详细信息，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。