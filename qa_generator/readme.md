# Dialogue Management Thesis: Test Set and Metrics for Local Collaborative Focus

This README provides an overview of the test set design and evaluation metrics for a thesis on **Dialogue Management** with a focus on **Local Collaborative** interactions. The data primarily involves retrieval-based information about a school, pre-embedded for efficient querying.

---

## **Objective**
The goal is to evaluate how well a dialogue management system handles **local collaborative tasks**, such as retrieving specific information (e.g., class schedules) while maintaining context across turns. The evaluation focuses on:
- **Local Context**: Ensuring responses are relevant to the immediate user query.
- **Global Context**: Maintaining coherence with the overall conversation flow.

---

## **Test Set Design**

### **1. Scenario-Based Test Cases**
Simulated conversations that mimic real-world interactions, focusing on local collaborative tasks:
- **Scenario 1**: Class Information Retrieval  
  - Turn 1: "Tell me about the Advanced Math class."  
  - Turn 2: "What is the schedule for this class?"  
  - *Goal*: Ensure the system retrieves and connects information from previous turns.  

- **Scenario 2**: Course Registration Workflow  
  - Turn 1: "I want to enroll in Physics 1."  
  - Turn 2: "Cancel that and switch to Chemistry 1."  
  - *Goal*: Test the system's ability to update context and handle task transitions.  

### **2. Edge Case Tests**
Challenging scenarios to evaluate robustness:
- **Ambiguous Queries**: "Is this class crowded?" → System should request clarification.  
- **Missing Information**: "When is the exam for this course?" → System should handle missing data gracefully.  
- **Sudden Topic Shifts**: From tuition fees to extracurricular activities → Test context-switching capabilities.  

---

## **Evaluation Metrics**

1. **Turn Accuracy**  
   - Measures the percentage of turns where the system provides accurate, locally relevant responses.  

2. **Context Consistency**  
   - Evaluates whether the system maintains context across multiple turns without "forgetting" prior information.  

3. **Task Completion Rate**  
   - Tracks the system's ability to guide users to their goals (e.g., successful course registration).  

4. **Retrieval Relevance**  
   - Compares system responses to ground truth using metrics like BLEU or ROUGE scores.  

---

## **Tools and Frameworks**
- **Evaluation Frameworks**: Use tools like [PyEval](https://github.com/PyEval) or [DialogRPT](https://github.com/facebookresearch/DialogRPT) for automated metric calculation.  
- **Data Simulation**: Generate test data using platforms like [Chatbot Arena](https://chatbotarena.ai/) or [ConvAI](https://convai.io/).  

---

## **Conclusion**
The test set is designed to comprehensively evaluate the **local collaborative** capabilities of a dialogue management system, ensuring it retrieves accurate information while maintaining conversational coherence. By combining scenario-based tests, edge cases, and robust metrics, this approach provides a clear framework for assessing system performance.

For more details, refer to the references below:
- [[1]] Dialogue State Tracking Techniques  
- [[6]] Contextual Consistency in Conversations  
- [[7]] Task-Oriented Dialogue Systems  
- [[8]] User Persona Modeling  