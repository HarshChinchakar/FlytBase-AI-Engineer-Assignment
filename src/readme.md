## Deployment & Hosting Notice

I sincerely apologize for not being able to locally host the complete project at this stage. However, all development, testing, and intermediate logs have been preserved and are accessible in the Kaggle notebook linked below:

🔗 [Kaggle Notebook: FlytBase Assignment](https://www.kaggle.com/code/harshchinchakar9921/flytbase-assignment)

Please feel free to notify me via email if access is restricted — I will ensure the notebook is made public temporarily to facilitate log review and evaluation.

---

### ⚠️ Dataset Limitation

Due to the lack of publicly available **docked drone surveillance footage**, I was unable to acquire a larger or more domain-specific dataset for testing. Consequently, the current implementation processes **only one sample input** that simulates a relevant security context.

Despite the dataset limitations, the full AI pipeline was built, tested, and successfully executed end-to-end.

---

### 🧪 Processing Performance (On Kaggle Hardware)

The entire pipeline was executed on **a single-threaded NVIDIA G100 GPU coupled with a CPU backend** using the Kaggle platform.

Here are the runtime statistics for the pipeline:

| Stage                  | Duration     |
|------------------------|--------------|
| ✅ Frame Extraction     | 8.20 seconds |
| ✅ Object Detection     | 19.11 seconds|
| ✅ Event Summarization  | 596.20 seconds |
| ✅ **Pipeline Status**  | Successfully Completed |

---

We appreciate your understanding regarding dataset constraints and hosting limitations. Despite these challenges, the solution demonstrates the functionality, modularity, and agentic intelligence expected for the assignment.


