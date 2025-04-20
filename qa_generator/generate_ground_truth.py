import openai
import json
import uuid

# Cấu hình API key (thay thế bằng API key của bạn)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Corpus thông tin (dựa trên website http://pgs.hcmut.edu.vn/)
corpus = {
    "notifications": [
        {
            "title": "Thông báo lịch thi HK2/2024-2025",
            "date": "02/04/2025",
            "url": "http://pgs.hcmut.edu.vn/vi/thong-bao/item/3222-thong-bao-lich-thi-hk2-2024-2025",
            "content": "Lịch thi học kỳ 2 năm học 2024-2025 đã được công bố."
        },
        {
            "title": "Thông báo nghỉ lễ Giỗ tổ Hùng Vương năm 2025",
            "date": "02/04/2025",
            "url": "http://pgs.hcmut.edu.vn/vi/thong-bao/thac-si-tai-bach-khoa/item/3223-thong-bao-nghi-le-gio-to-hung-vuong-nam-2025",
            "content": "Thông báo lịch nghỉ lễ Giỗ tổ Hùng Vương năm 2025."
        },
        {
            "title": "Học bổng tại Rumani năm 2025",
            "date": "04/04/2025",
            "url": "http://pgs.hcmut.edu.vn/vi/thong-bao/thong-tin-chung/item/3227-hoc-bong-tai-rumani-nam-2025",
            "content": "Thông tin về học bổng tại Rumani năm 2025."
        },
        {
            "title": "Tuyển sinh đào tạo trình độ thạc sĩ đợt tháng 06 năm 2025",
            "date": "06/03/2025",
            "url": "http://pgs.hcmut.edu.vn/vi/tuyen-sinh/thac-si/thong-tin-tuyen-sinh-thac-si",
            "content": "Thông tin đăng ký tuyển sinh thạc sĩ tháng 06/2025."
        },
        {
            "title": "Kế hoạch nộp chứng chỉ ngoại ngữ, xét tốt nghiệp tháng 4/2025",
            "date": "24/02/2025",
            "url": "http://pgs.hcmut.edu.vn/vi/thong-bao/thong-tin-chung/item/3193-ke-hoach-nop-chung-chi-ngoai-ngu-nop-ho-so-xet-tot-nghiep-thang-04-2025",
            "content": "Kế hoạch nộp chứng chỉ ngoại ngữ và hồ sơ xét tốt nghiệp."
        }
    ],
    "contact": {
        "email": "sdh@hcmut.edu.vn",
        "phone": "(+84) 766 780 247",
        "address": "268 Lý Thường Kiệt, Quận 10, TP.HCM"
    }
}

def generate_test_case(dialogue_id, scenario):
    # Prompt yêu cầu LLM tạo test case
    prompt = f"""
    Bạn là một trợ lý AI chuyên về quản lý đối thoại. Nhiệm vụ của bạn là tạo một test case đối thoại multi-turn (3-5 lượt) dựa trên kịch bản sau: '{scenario}'.
    Dữ liệu được lấy từ Cổng Thông Tin Đào Tạo Sau Đại Học - Đại Học Bách Khoa TP.HCM (http://pgs.hcmut.edu.vn/). Dưới đây là một phần corpus:

    {json.dumps(corpus, ensure_ascii=False, indent=2)}

    **Yêu cầu**:
    - Tạo một đoạn đối thoại multi-turn mô phỏng tình huống thực tế, với user_input và llm_response.
    - Mỗi lượt phải có nhãn (labels) bao gồm:
      - knowledge_reference: URL hoặc tiêu đề của thông tin trong corpus được sử dụng.
      - accuracy: 1 nếu phản hồi chính xác, 0 nếu sai.
      - coherence: Điểm từ 1-5 (5 là mạch lạc nhất).
      - collaboration: Điểm từ 1-5 (5 là hỗ trợ người dùng tốt nhất).
    - Đảm bảo tập trung vào khả năng 'local collaborative' (hợp tác tại từng lượt).
    - Trả về định dạng JSON với dialogue_id là {dialogue_id}.

    **Ví dụ định dạng**:
    ```json
    {
      "dialogue_id": 1,
      "description": "Học viên hỏi về lịch thi.",
      "turns": [
        {
          "turn_id": 1,
          "user_input": "Lịch thi HK2/2024-2025 là khi nào?",
          "llm_response": "Lịch thi đã được công bố ngày 02/04/2025, xem tại ...",
          "labels": {
            "knowledge_reference": "URL hoặc tiêu đề",
            "accuracy": 1,
            "coherence": 5,
            "collaboration": 5
          }
        }
      ]
    }
    ```

    Hãy tạo test case cho kịch bản: '{scenario}'.
    """

    # Gọi API OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI chuyên tạo dữ liệu đối thoại."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    # Lấy nội dung JSON từ phản hồi
    test_case = json.loads(response.choices[0].message.content)
    return test_case

def main():
    # Danh sách các kịch bản để tạo 10 test case
    scenarios = [
        "Học viên hỏi về lịch thi học kỳ 2 năm học 2024-2025 và cách tra cứu.",
        "Học viên hỏi về học bổng sau đại học năm 2025 và yêu cầu chứng chỉ ngoại ngữ.",
        "Học viên hỏi về đăng ký tuyển sinh thạc sĩ năm 2025 và lớp ôn tập.",
        "Học viên hỏi về lịch nghỉ lễ và thay đổi phòng học năm 2025.",
        "Học viên hỏi về luận văn thạc sĩ và kế hoạch đánh giá đợt 13/01/2025.",
        "Học viên hỏi về đăng ký môn học học kỳ 2 năm 2024-2025 cho nghiên cứu sinh.",
        "Học viên hỏi về hội đồng đánh giá luận án tiến sĩ và đăng ký đề tài nghiên cứu.",
        "Học viên hỏi về cơ hội thực tập và học bổng Manaaki của New Zealand.",
        "Học viên hỏi về tra cứu văn bằng thạc sĩ và quy định đào tạo.",
        "Học viên hỏi về khóa tập huấn và seminar cho nghiên cứu sinh."
    ]

    test_cases = []
    for i, scenario in enumerate(scenarios, 1):
        test_case = generate_test_case(i, scenario)
        test_cases.append(test_case)

    # Lưu test cases vào JSON
    output = {
        "test_cases": test_cases
    }

    # In kết quả (hoặc lưu vào file)
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # Lưu vào file (tùy chọn)
    with open("test_cases.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()