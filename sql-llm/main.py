from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import torch
import deepspeed

# Create ds_config.json file
ds_config = {
    "fp16": {
        "enabled": True,
        "loss_scale": 0,
        "loss_scale_window": 1000,
        "initial_scale_power": 16,
        "hysteresis": 2,
        "min_loss_scale": 1,
    },
    "optimizer": {
        "type": "AdamW",
        "params": {
            "lr": 2e-5,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay": 0.01,
        },
    },
    "scheduler": {
        "type": "WarmupDecayLR",
        "params": {
            "warmup_min_lr": 0,
            "warmup_max_lr": 2e-5,
            "warmup_num_steps": 500,
            "total_num_steps": 5000,
        },
    },
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {"device": "cpu", "pin_memory": True},
        "allgather_partitions": True,
        "allgather_bucket_size": 2e8,
        "overlap_comm": True,
        "reduce_scatter": True,
        "reduce_bucket_size": 2e8,
        "contiguous_gradients": True,
    },
    "gradient_accumulation_steps": 2,
    "steps_per_print": 100,
    "train_batch_size": 4,
    "wall_clock_breakdown": False,
}

# Save config
import json

with open("ds_config.json", "w") as f:
    json.dump(ds_config, f)

# Load model with DeepSpeed integration
model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf",
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16,
)

# Add LoRA adapters
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("gretelai/synthetic_text_to_sql", split="train")

# Modified TrainingArguments for DeepSpeed
training_args = TrainingArguments(
    output_dir="./sql-expert",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    optim="adamw_torch",
    save_steps=500,
    logging_steps=100,
    learning_rate=2e-5,
    fp16=True,
    gradient_checkpointing=True,
    max_steps=5000,
    deepspeed="./ds_config.json",  # DeepSpeed config
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=lambda data: {
        "input_ids": torch.stack([d["input_ids"] for d in data]),
        "attention_mask": torch.stack([d["attention_mask"] for d in data]),
        "labels": torch.stack([d["labels"] for d in data]),
    },
)

# Launch training with DeepSpeed
trainer.train()
