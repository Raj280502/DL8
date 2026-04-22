"""
Medical Report Generation using LangChain and Groq LLM.
Generates comprehensive clinical reports for brain tumor, stroke, and Alzheimer analysis.
"""

import os
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _require_env(keys: list) -> str:
    """Get first available environment variable."""
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    joined = ", ".join(keys)
    raise EnvironmentError(f"Missing required environment variable(s): {joined}")


@lru_cache(maxsize=1)
def _get_report_llm():
    """Get cached Groq LLM instance."""
    try:
        api_key = _require_env(["GROQ_API_KEY"])
        llm = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",  # Lightweight but capable model
            temperature=0.3,
            max_tokens=1024,
        )
        print("✅ Groq LLM initialized with llama-3.1-8b-instant")
        return llm
    except EnvironmentError as e:
        print(f"⚠️  Groq API key not configured: {e}")
        print("⚠️  Using fallback template-based reports")
        return None


def _create_brain_tumor_prompt(result: Dict[str, Any]) -> ChatPromptTemplate:
    """Create prompt template for brain tumor detection report."""
    template = """
Generate a professional medical report for brain tumor detection analysis.

Analysis Results:
- Total Detections: {num_detections}
- Detections: {detections}
- Confidence Threshold Used: 0.4

Instructions:
1. Start with a brief "FINDINGS" section summarizing the detection results
2. Include a "TUMOR DETAILS" section listing each detected tumor with location and confidence
3. Add a "CLINICAL SIGNIFICANCE" section explaining what these findings mean
4. Provide "RECOMMENDATIONS" for follow-up imaging or consultation
5. End with "DISCLAIMER" stating this is for research purposes only

Be professional, concise, and evidence-based. Use medical terminology appropriately.
"""
    return ChatPromptTemplate.from_template(template)


def _create_stroke_prompt(result: Dict[str, Any]) -> ChatPromptTemplate:
    """Create prompt template for stroke classification report."""
    template = """
Generate a professional medical report for stroke classification analysis.

Analysis Results:
- Predicted Class: {predicted_class}
- Confidence: {confidence:.1%}
- Hemorrhagic Probability: {hemorrhagic:.1%}
- Ischemic Probability: {ischemic:.1%}
- Normal Probability: {normal:.1%}
- Clinical Fusion Applied: {fusion_applied}
{clinical_note}

Instructions:
1. Start with "FINDINGS" - clearly state the classification result
2. Include "CONFIDENCE ASSESSMENT" - explain the confidence level
3. Add "CLINICAL INTERPRETATION" - what this classification means for stroke type
4. Provide "DIFFERENTIAL DIAGNOSIS" - briefly discuss alternative possibilities
5. Include "RECOMMENDATIONS" for further evaluation or consultation
6. End with "DISCLAIMER" - state this is for research purposes only

Be clear, medically sound, and appropriately cautious. Use appropriate medical terminology.
"""
    return ChatPromptTemplate.from_template(template)


def _create_alzheimer_prompt(result: Dict[str, Any]) -> ChatPromptTemplate:
    """Create prompt template for Alzheimer classification report."""
    template = """
Generate a professional medical report for Alzheimer's disease classification analysis.

Analysis Results:
- Predicted Stage: {predicted_class}
- Confidence: {confidence:.1%}
- Non Demented: {non_demented:.1%}
- Very Mild Demented: {very_mild:.1%}
- Mild Demented: {mild:.1%}
- Moderate Demented: {moderate:.1%}
- Multimodal Fusion Applied: {fusion_applied}
{clinical_note}

Instructions:
1. Start with "CLINICAL ASSESSMENT" - state the predicted Alzheimer's stage
2. Include "IMAGING ANALYSIS" - explain what the brain scan shows
3. Add "DEMENTIA STAGING" - explain the severity level predicted
4. Provide "CLINICAL CORRELATION" - how this relates to cognitive symptoms
5. Include "RECOMMENDATIONS" for follow-up evaluations and clinical consultation
6. End with "DISCLAIMER" - clearly state this requires comprehensive clinical evaluation

Be empathetic yet professional. Emphasize the need for full clinical assessment. Use appropriate terminology.
"""
    return ChatPromptTemplate.from_template(template)


def generate_brain_tumor_report(result: Dict[str, Any]) -> str:
    """
    Generate a medical report for brain tumor detection results.

    Args:
        result: Dict containing predictions from predict_brain_tumor()

    Returns:
        str: Generated medical report
    """
    try:
        llm = _get_report_llm()
        if llm is None:
            return _generate_fallback_brain_tumor_report(result)

        predictions = result.get("predictions", [])
        num_detections = len(predictions)

        detections_str = "\n".join([
            f"  - {p['name']}: confidence {p['confidence']:.2%} at location ({p['xmin']:.0f}, {p['ymin']:.0f}) to ({p['xmax']:.0f}, {p['ymax']:.0f})"
            for p in predictions
        ]) if predictions else "No tumors detected"

        prompt_template = _create_brain_tumor_prompt(result)

        chain = prompt_template | llm | StrOutputParser()
        report = chain.invoke({
            "num_detections": num_detections,
            "detections": detections_str
        })

        return report.strip()
    except Exception as e:
        print(f"⚠️  Error generating brain tumor report with LLM: {e}")
        print("⚠️  Using fallback template-based report")
        return _generate_fallback_brain_tumor_report(result)


def generate_stroke_report(result: Dict[str, Any]) -> str:
    """
    Generate a medical report for stroke classification results.

    Args:
        result: Dict containing predictions from predict_stroke()

    Returns:
        str: Generated medical report
    """
    try:
        llm = _get_report_llm()
        if llm is None:
            return _generate_fallback_stroke_report(result)

        class_confidences = result.get("class_confidences", {})
        predicted_class = result.get("predicted_class", "Unknown")
        confidence = result.get("confidence", 0.0)
        fusion_applied = result.get("fusion_applied", False)
        clinical_inputs = result.get("clinical_inputs", {})

        hemorrhagic = class_confidences.get("Hemorrhagic", 0.0)
        ischemic = class_confidences.get("Ischemic", 0.0)
        normal = class_confidences.get("Normal", 0.0)

        clinical_note = ""
        if fusion_applied and clinical_inputs:
            age = clinical_inputs.get("age")
            clinical_note = f"\nClinical Data Used for Fusion:\n- Patient Age: {age} years"

        prompt_template = _create_stroke_prompt(result)
        chain = prompt_template | llm | StrOutputParser()

        report = chain.invoke({
            "predicted_class": predicted_class,
            "confidence": confidence,
            "hemorrhagic": hemorrhagic,
            "ischemic": ischemic,
            "normal": normal,
            "fusion_applied": "Yes (Image + Clinical Data)" if fusion_applied else "No",
            "clinical_note": clinical_note
        })

        return report.strip()
    except Exception as e:
        print(f"⚠️  Error generating stroke report with LLM: {e}")
        print("⚠️  Using fallback template-based report")
        return _generate_fallback_stroke_report(result)


def generate_alzheimer_report(result: Dict[str, Any]) -> str:
    """
    Generate a medical report for Alzheimer classification results.

    Args:
        result: Dict containing predictions from predict_alzheimer()

    Returns:
        str: Generated medical report
    """
    try:
        llm = _get_report_llm()
        if llm is None:
            return _generate_fallback_alzheimer_report(result)

        class_confidences = result.get("class_confidences", {})
        predicted_class = result.get("predicted_class", "Unknown")
        confidence = result.get("confidence", 0.0)
        fusion_applied = result.get("fusion_applied", False)
        clinical_inputs = result.get("clinical_inputs", {})

        non_demented = class_confidences.get("Non Demented", 0.0)
        very_mild = class_confidences.get("Very Mild Demented", 0.0)
        mild = class_confidences.get("Mild Demented", 0.0)
        moderate = class_confidences.get("Moderate Demented", 0.0)

        clinical_note = ""
        if fusion_applied and clinical_inputs:
            age = clinical_inputs.get("age")
            mmse = clinical_inputs.get("mmse_score")
            clinical_note = f"\nClinical Data Used for Multimodal Fusion:"
            if age:
                clinical_note += f"\n- Patient Age: {age} years"
            if mmse is not None:
                clinical_note += f"\n- MMSE Score: {mmse}/30"

        prompt_template = _create_alzheimer_prompt(result)
        chain = prompt_template | llm | StrOutputParser()

        report = chain.invoke({
            "predicted_class": predicted_class,
            "confidence": confidence,
            "non_demented": non_demented,
            "very_mild": very_mild,
            "mild": mild,
            "moderate": moderate,
            "fusion_applied": "Yes (Image + Clinical Data)" if fusion_applied else "No (Image Only)",
            "clinical_note": clinical_note
        })

        return report.strip()
    except Exception as e:
        print(f"⚠️  Error generating Alzheimer report with LLM: {e}")
        print("⚠️  Using fallback template-based report")
        return _generate_fallback_alzheimer_report(result)


# Fallback report generators (no LLM needed)
def _generate_fallback_brain_tumor_report(result: Dict[str, Any]) -> str:
    """Generate fallback report when LLM is unavailable."""
    predictions = result.get("predictions", [])
    num_detections = len(predictions)

    report = f"""
BRAIN TUMOR DETECTION REPORT
{'=' * 50}

FINDINGS:
Number of tumors detected: {num_detections}

TUMOR DETAILS:
"""
    if predictions:
        for i, pred in enumerate(predictions, 1):
            report += f"\nTumor {i}:\n"
            report += f"  Type: {pred.get('name', 'Unknown')}\n"
            report += f"  Confidence: {pred.get('confidence', 0.0):.2%}\n"
            report += f"  Location: ({pred['xmin']:.0f}, {pred['ymin']:.0f}) to ({pred['xmax']:.0f}, {pred['ymax']:.0f})\n"
    else:
        report += "No brain tumors detected in the analysis.\n"

    report += f"""
RECOMMENDATIONS:
- Further imaging evaluation recommended based on findings
- Clinical correlation with patient symptoms is essential
- Consult with a neuroradiologist for detailed assessment

DISCLAIMER:
This analysis is generated for research purposes only. It should not be used
for clinical diagnosis. Always consult with qualified medical professionals
for proper interpretation of medical imaging.
"""
    return report


def _generate_fallback_stroke_report(result: Dict[str, Any]) -> str:
    """Generate fallback report for stroke when LLM is unavailable."""
    predicted_class = result.get("predicted_class", "Unknown")
    confidence = result.get("confidence", 0.0)
    class_confidences = result.get("class_confidences", {})

    report = f"""
STROKE CLASSIFICATION REPORT
{'=' * 50}

FINDINGS:
Predicted Stroke Type: {predicted_class}
Confidence Level: {confidence:.1%}

CLASSIFICATION PROBABILITIES:
- Hemorrhagic: {class_confidences.get('Hemorrhagic', 0.0):.1%}
- Ischemic: {class_confidences.get('Ischemic', 0.0):.1%}
- Normal: {class_confidences.get('Normal', 0.0):.1%}

CLINICAL INTERPRETATION:
The analysis suggests a {predicted_class.lower()} classification with {confidence:.1%} confidence.

RECOMMENDATIONS:
- Immediate clinical assessment recommended
- Additional diagnostic tests may be necessary
- Consult with a stroke specialist for proper evaluation
- Time-critical treatment may be required

DISCLAIMER:
This AI analysis is for research purposes only and should not be used for
clinical diagnosis. Always consult with qualified medical professionals for
proper interpretation and immediate medical attention for suspected stroke.
"""
    return report


def _generate_fallback_alzheimer_report(result: Dict[str, Any]) -> str:
    """Generate fallback report for Alzheimer when LLM is unavailable."""
    predicted_class = result.get("predicted_class", "Unknown")
    confidence = result.get("confidence", 0.0)
    class_confidences = result.get("class_confidences", {})
    fusion_applied = result.get("fusion_applied", False)

    report = f"""
ALZHEIMER'S DISEASE CLASSIFICATION REPORT
{'=' * 50}

CLINICAL ASSESSMENT:
Predicted Stage: {predicted_class}
Confidence: {confidence:.1%}

DEMENTIA PROBABILITIES:
- Non Demented: {class_confidences.get('Non Demented', 0.0):.1%}
- Very Mild Demented: {class_confidences.get('Very Mild Demented', 0.0):.1%}
- Mild Demented: {class_confidences.get('Mild Demented', 0.0):.1%}
- Moderate Demented: {class_confidences.get('Moderate Demented', 0.0):.1%}

IMAGING ANALYSIS:
Brain MRI shows findings consistent with {predicted_class.lower()} status.

RECOMMENDATIONS:
- Comprehensive cognitive assessment recommended
- Follow-up MRI imaging in 6-12 months
- Neuropsychological testing advised
- Consult with a neurologist for proper evaluation

DISCLAIMER:
This AI analysis is for research purposes only. Alzheimer's disease diagnosis
requires comprehensive clinical evaluation including cognitive assessments,
medical history, and professional medical consultation. This report should not
be used for clinical diagnosis without proper medical evaluation.
"""
    return report
