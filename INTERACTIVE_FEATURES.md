# Interactive Features Guide

## Overview

The Image Auto-Tagger now supports interactive mode for enhanced user experience, allowing you to:

- **Choose from multiple Gemini models** at startup
- **Configure API keys** interactively or via command line
- **Seamless integration** with existing functionality

## Available Gemini Models

| Model ID | Description | Use Case |
|----------|-------------|----------|
| `gemini-2.5-flash-preview` | Gemini 2.5 Flash Preview | Latest preview features |
| `gemini-2.0-flash-exp` | Gemini 2.0 Flash (Experimental) | Latest experimental features |
| `gemini-1.5-flash` | Gemini 1.5 Flash (Default) | Fast processing, good balance |
| `gemini-1.5-pro` | Gemini 1.5 Pro | Enhanced accuracy and capabilities |
| `gemini-1.5-pro-latest` | Gemini 1.5 Pro Latest | Latest stable pro version |

## Usage Examples

### Interactive Mode

```bash
# Enable interactive mode for model selection and API key input
python src/main.py ./imgs --interactive
```

This will prompt you to:
1. Select a Gemini model from the available options
2. Choose API key configuration method

### Command Line Options

```bash
# Specify model and API key directly
python src/main.py ./imgs --gemini-model gemini-1.5-flash --gemini-api-key YOUR_API_KEY

# Use specific model with environment variable API key
python src/main.py ./imgs --gemini-model gemini-1.5-pro

# Interactive model selection only (API key from environment)
python src/main.py ./imgs --interactive --gemini-api-key YOUR_API_KEY
```

### Environment Variables

```bash
# Set API key as environment variable (recommended)
export GEMINI_API_KEY="your_api_key_here"
python src/main.py ./imgs
```

## Interactive Prompts

### Model Selection

```
🤖 Available Gemini Models:
  1. Gemini 2.5 Flash Preview
  2. Gemini 2.0 Flash (Experimental)
  3. Gemini 1.5 Flash (Default)
  4. Gemini 1.5 Pro
  5. Gemini 1.5 Pro Latest

Select model (1-5, or press Enter for default):
```

### API Key Configuration

```
🔑 Gemini API Key Configuration:
  1. Use environment variable GEMINI_API_KEY (Default)
  2. Enter API key manually

Select option (1-2, or press Enter for default):
```

## Command Line Arguments

### New Arguments

| Argument | Description | Example |
|----------|-------------|----------|
| `--interactive` | Enable interactive mode | `--interactive` |
| `--gemini-model` | Specify Gemini model | `--gemini-model gemini-1.5-pro` |
| `--gemini-api-key` | Provide API key directly | `--gemini-api-key YOUR_KEY` |

### Existing Arguments (Updated)

| Argument | Description | Default |
|----------|-------------|----------|
| `input_path` | Path to image file or directory | Required |
| `-c, --credentials` | Google Cloud credentials JSON file | Optional |
| `-o, --output` | Output JSON file path | Auto-generated |
| `-l, --lang` | Language code for output | `FR` |
| `-w, --workers` | Number of parallel workers | `1` |
| `-v, --verbose` | Increase verbosity level | `1` |
| `-r, --rename` | Rename files based on analysis | `False` |
| `--retries` | Number of API retry attempts | `3` |
| `--api` | API to use (vision, gemini, both) | `both` |

## Testing

### Test Interactive Features

```bash
# Run the interactive features test
python test_interactive.py
```

This test script will:
1. Display available models
2. Test interactive model selection
3. Test interactive API key configuration
4. Show usage examples

### Test with Real Images

```bash
# Test with interactive mode
python src/main.py ./imgs --interactive

# Test with specific model
python debug_test.py  # Uses default configuration
```

## Security Best Practices

1. **Environment Variables**: Use `GEMINI_API_KEY` environment variable for API keys
2. **Avoid Command Line**: Don't pass API keys via command line in production
3. **Secure Storage**: Store API keys securely, never commit them to version control
4. **Key Masking**: The application masks API keys in logs and output

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   ⚠️ GEMINI_API_KEY not found in environment variables
   ```
   **Solution**: Set the environment variable or use interactive mode

2. **Invalid Model Selection**
   ```
   ❌ Invalid selection. Please choose 1-4.
   ```
   **Solution**: Enter a number between 1-4 or press Enter for default

3. **Quota Exceeded**
   ```
   ResourceExhausted - 429 You exceeded your current quota
   ```
   **Solution**: Check your Gemini API billing and quotas

### Debug Mode

```bash
# Enable verbose logging
python src/main.py ./imgs --interactive -vv
```

## Integration Notes

- **Backward Compatibility**: All existing functionality remains unchanged
- **Default Behavior**: Without `--interactive`, uses environment variables or defaults
- **Graceful Fallbacks**: Handles missing configurations gracefully
- **Error Handling**: Comprehensive error handling for user inputs

## Future Enhancements

- Configuration file support
- Model performance comparison
- Batch processing with different models
- Advanced retry strategies per model