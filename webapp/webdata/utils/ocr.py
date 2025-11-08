from PIL import Image
import pytesseract
import re
from webdata.config import Config
import os

pytesseract.pytesseract.tesseract_cmd = f"{Config.TESSERACT_CMD_PATH}"

def ocr_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    print(f"OCR Extracted for: {os.path.basename(image_path)}")
    return text

# def parse_ocr_result(text):
#     """
#     Parses OCR text from a network report.

#     If the text is invalid (missing the 'Destination Networks' marker),
#     it returns a dictionary with all values set to 'Not Available'
#     instead of raising an error.
#     """
#     # Define all possible keys for the output dictionary. This makes it easy to
#     # create a consistent "Not Available" response.
#     ALL_KEYS = [
#         'Title', 'Time Range', 'Source Device', 'Source Device IP',
#         'In Interface', 'Description', 'Speed', 'Dest Subnet', 'Dest Mask',
#         'Peak Traffic Rate', 'Peak Traffic Time', 'Average Traffic', 'Average Data'
#     ]

#     # Clean up input lines
#     lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

#     # If the input is empty after stripping, it's invalid.
#     if not lines:
#         return {key: "Not Available" for key in ALL_KEYS}

#     # Find the index of the "Destination Networks" line.
#     # If it's not found, we consider the file invalid and return a "Not Available" dict.
#     try:
#         dest_net_idx = lines.index('Destination Networks')
#     except ValueError:
#         # MODIFICATION: Instead of raising an error, return a dictionary
#         # indicating that the data is not available for this input.
#         return {key: "Not Available" for key in ALL_KEYS}

#     # Initialize the result dictionary with empty strings for all keys.
#     # This is cleaner than adding them one by one.
#     result = {key: '' for key in ALL_KEYS}

#     # --- Start Parsing ---

#     # Parse Title
#     title = ' - '.join(lines[:dest_net_idx])
#     result['Title'] = title

#     # Find the 'Traffic Rate' section index (it's optional)
#     try:
#         traffic_rate_idx = lines.index('Traffic Rate')
#     except ValueError:
#         traffic_rate_idx = None

#     # Parse fields between "Destination Networks" and "Traffic Rate"
#     field_patterns = {
#         'Time Range':      r'Time range:\s*(.*)',
#         'Source Device':   r'Source device:\s*([^\s]+)\s*\(([^)]+)\)',
#         'In Interface':    r'In interface:\s*(.*)',
#         'Description':     r'Description:\s*(.*)',
#         'Speed':           r'Speed:\s*(.*)',
#         'Dest Subnet':     r'Dest subnet:\s*(.*)',
#         'Dest Mask':       r'Dest mask:\s*(.*)',
#     }

#     scan_end = traffic_rate_idx if traffic_rate_idx is not None else len(lines)
#     for line in lines[dest_net_idx+1:scan_end]:
#         for key, pattern in field_patterns.items():
#             m = re.match(pattern, line)
#             if m:
#                 if key == 'Source Device':
#                     result['Source Device'] = m.group(1)
#                     result['Source Device IP'] = m.group(2)
#                 else:
#                     result[key] = m.group(1)
#                 break # Move to the next line once a pattern is matched

#     # Parse the "Traffic Rate" section if it exists
#     if traffic_rate_idx is not None:
#         # Find "Dest. Subnet Traffic Rate - Peak"
#         peak_idx = None
#         for i in range(traffic_rate_idx + 1, len(lines)):
#             if lines[i].startswith('Dest. Subnet Traffic Rate - Peak'):
#                 peak_idx = i
#                 break

#         # Parse Peak line
#         if peak_idx is not None and peak_idx + 1 < len(lines):
#             peak_line = re.sub(r'^[| ]+', '', lines[peak_idx + 1]) # Remove leading junk
#             m = re.match(r'[\d\.\/]+\s+([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', peak_line, re.IGNORECASE)
#             if m:
#                 result['Peak Traffic Rate'] = m.group(1).replace(' ', '')
#                 result['Peak Traffic Time'] = m.group(2)

#         # Parse Average line
#         start_avg_scan = peak_idx + 2 if peak_idx is not None else traffic_rate_idx + 1
#         for i in range(start_avg_scan, len(lines)):
#             avg_line = re.sub(r'^[| ]+', '', lines[i]) # Remove leading junk
#             m = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line, re.IGNORECASE)
#             if m:
#                 result['Average Traffic'] = m.group(1).replace(' ', '')
#                 result['Average Data'] = m.group(2)
#                 break
#             # Handle case where "Average" is on its own line
#             if avg_line.lower() == "average" and i + 1 < len(lines):
#                 avg_line2 = re.sub(r'^[| ]+', '', lines[i + 1])
#                 m2 = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line2, re.IGNORECASE)
#                 if m2:
#                     result['Average Traffic'] = m2.group(1).replace(' ', '')
#                     result['Average Data'] = m2.group(2)
#                     break

#     # Final cleanup for Average Data
#     if result['Average Data'].startswith('(') and result['Average Data'].endswith(')'):
#         result['Average Data'] = result['Average Data'][1:-1]
#     return result

# def parse_ocr_result(text):
#     result = {}

#     lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

#     # Find indices
#     try:
#         dest_net_idx = lines.index('Destination Networks')
#     except ValueError:
#         raise ValueError("Missing 'Destination Networks' in input.")

#     try:
#         traffic_rate_idx = lines.index('Traffic Rate')
#     except ValueError:
#         traffic_rate_idx = None

#     title = ' - '.join(lines[:dest_net_idx])
#     result['Title'] = title

#     field_patterns = {
#         'Time Range':      r'Time range:\s*(.*)',
#         'Source Device':   r'Source device:\s*([^\s]+)\s*\(([^)]+)\)',
#         'In Interface':    r'In interface:\s*(.*)',
#         'Description':     r'Description:\s*(.*)',
#         'Speed':           r'Speed:\s*(.*)',
#         'Dest Subnet':     r'Dest subnet:\s*(.*)',
#         'Dest Mask':       r'Dest mask:\s*(.*)',
#     }
#     field_values = {}

#     scan_end = traffic_rate_idx if traffic_rate_idx is not None else len(lines)
#     for line in lines[dest_net_idx+1:scan_end]:
#         for k, pattern in field_patterns.items():
#             m = re.match(pattern, line)
#             if m:
#                 if k == 'Source Device':
#                     field_values['Source Device'] = m.group(1)
#                     field_values['Source Device IP'] = m.group(2)
#                 else:
#                     field_values[k] = m.group(1)
#                 break

#     for k in ['Time Range', 'Source Device', 'Source Device IP', 'In Interface', 'Description', 'Speed', 'Dest Subnet', 'Dest Mask']:
#         result[k] = field_values.get(k, '')

#     result['Peak Traffic Rate'] = ''
#     result['Peak Traffic Time'] = ''
#     result['Average Traffic'] = ''
#     result['Average Data'] = ''

#     if traffic_rate_idx is not None:
#         # Find "Dest. Subnet Traffic Rate - Peak"
#         peak_idx = None
#         for i in range(traffic_rate_idx+1, len(lines)):
#             if lines[i].startswith('Dest. Subnet Traffic Rate - Peak'):
#                 peak_idx = i
#                 break

#         # Peak line
#         if peak_idx is not None and peak_idx+1 < len(lines):
#             peak_line = lines[peak_idx+1]
#             # Remove leading junk (|, ||, spaces)
#             peak_line = re.sub(r'^[| ]+', '', peak_line)
#             # Try to match: <subnet> <rate> (<time>)
#             m = re.match(r'[\d\.\/]+\s+([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', peak_line, re.IGNORECASE)
#             if m:
#                 result['Peak Traffic Rate'] = m.group(1).replace(' ', '')
#                 result['Peak Traffic Time'] = m.group(2)
#         # Average line
#         for i in range(peak_idx+2 if peak_idx is not None else traffic_rate_idx+1, len(lines)):
#             # Remove leading junk
#             avg_line = re.sub(r'^[| ]+', '', lines[i])
#             m = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line, re.IGNORECASE)
#             if m:
#                 result['Average Traffic'] = m.group(1).replace(' ', '')
#                 result['Average Data'] = m.group(2)
#                 break
#             # Sometimes Average line is just "Average" and the value is on the next line
#             if avg_line.lower() == "average" and i+1 < len(lines):
#                 avg_line2 = re.sub(r'^[| ]+', '', lines[i+1])
#                 m2 = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line2, re.IGNORECASE)
#                 if m2:
#                     result['Average Traffic'] = m2.group(1).replace(' ', '')
#                     result['Average Data'] = m2.group(2)
#                     break

#     # Remove parentheses from Average Data if present
#     if result['Average Data'].startswith('(') and result['Average Data'].endswith(')'):
#         result['Average Data'] = result['Average Data'][1:-1]

#     return result




def convert_to_kbps(rate_string):
    """
    Converts a traffic rate string (e.g., "1.2 Mbps", "500 bps") to a
    numeric value in Kbps.

    Args:
        rate_string (str): The traffic rate string with units.

    Returns:
        str: The numeric value in Kbps as a string, or an empty string
             if conversion is not possible.
    """
    if not isinstance(rate_string, str) or not rate_string:
        return ''

    # Normalize the string: lowercase, remove spaces
    norm_string = rate_string.lower().replace(' ', '')

    # Define multipliers to convert to Kbps
    unit_multipliers = {
        'tbps': 1000 * 1000 * 1000,
        'gbps': 1000 * 1000,
        'mbps': 1000,
        'kbps': 1,
        'bps': 0.001,
    }

    for unit, multiplier in unit_multipliers.items():
        if norm_string.endswith(unit):
            numeric_part_str = norm_string[:-len(unit)]
            try:
                value = float(numeric_part_str)
                # Return the converted value as a string
                return str(value * multiplier)
            except (ValueError, TypeError):
                # If the numeric part isn't a valid number
                return ''

    # If no known unit was found
    return ''


def parse_ocr_result(text):
    """
    Parses OCR text from a network report.

    If the text is invalid (missing the 'Destination Networks' marker),
    it returns a dictionary with all values set to 'Not Available'
    instead of raising an error.

    MODIFICATION: Traffic rates are converted to Kbps and their keys are renamed.
    MODIFICATION: Time Range is split into Time Date and Analytics Time.
    """
    # Define all possible keys for the output dictionary. This makes it easy to
    # create a consistent "Not Available" response.
    # MODIFICATION: Renamed traffic rate keys and split Time Range.
    ALL_KEYS = [
        'Title', 'Time Date', 'Analytics Time', 'Source Device', 'Source Device IP',
        'In Interface', 'Description', 'Speed', 'Dest Subnet', 'Dest Mask',
        'Peak Traffic Rate (in Kbps)', 'Peak Traffic Time', 'Average Traffic (kbps)', 'Average Data'
    ]

    # Clean up input lines
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    # If the input is empty after stripping, it's invalid.
    if not lines:
        return {key: "" for key in ALL_KEYS}

    # Find the index of the "Destination Networks" line.
    # If it's not found, we consider the file invalid and return a "Not Available" dict.
    try:
        dest_net_idx = lines.index('Destination Networks')
    except ValueError:
        return {key: "" for key in ALL_KEYS}

    # Initialize the result dictionary with empty strings for all keys.
    result = {key: '' for key in ALL_KEYS}

    # --- Start Parsing ---

    # Parse Title
    title = ' - '.join(lines[:dest_net_idx])
    result['Title'] = title

    # Find the 'Traffic Rate' section index (it's optional)
    try:
        traffic_rate_idx = lines.index('Traffic Rate')
    except ValueError:
        traffic_rate_idx = None

    # Parse fields between "Destination Networks" and "Traffic Rate"
    # MODIFICATION: Removed 'Time Range' as it's now handled specially.
    field_patterns = {
        'Source Device':   r'Source device:\s*([^\s]+)\s*\(([^)]+)\)',
        'In Interface':    r'In interface:\s*(.*)',
        'Description':     r'Description:\s*(.*)',
        'Speed':           r'Speed:\s*(.*)',
        'Dest Subnet':     r'Dest subnet:\s*(.*)',
        'Dest Mask':       r'Dest mask:\s*(.*)',
    }

    scan_end = traffic_rate_idx if traffic_rate_idx is not None else len(lines)
    for line in lines[dest_net_idx+1:scan_end]:
        # --- MODIFICATION START: Special handling for Time Range ---
        if line.lower().startswith('time range:'):
            full_time_range_str = line.split(':', 1)[1].strip()
            # Expecting format like: "Jul 9, 2025, 8:00 AM WIB - 5:00 PM WIB"
            # We split by comma a maximum of 2 times to separate date and time parts.
            parts = full_time_range_str.split(',', 2)
            if len(parts) == 3:
                # Re-join the first two parts for the full date
                result['Time Date'] = f"{parts[0]},{parts[1]}".strip()
                result['Analytics Time'] = parts[2].strip()
            else:
                # Fallback if format is unexpected
                result['Time Date'] = full_time_range_str
                result['Analytics Time'] = "Not Available"
            continue # Skip to the next line
        # --- MODIFICATION END ---

        # Original loop for other patterns
        for key, pattern in field_patterns.items():
            m = re.match(pattern, line)
            if m:
                if key == 'Source Device':
                    result['Source Device'] = m.group(1)
                    result['Source Device IP'] = m.group(2)
                else:
                    result[key] = m.group(1)
                break # Move to the next line once a pattern is matched

    # Parse the "Traffic Rate" section if it exists
    if traffic_rate_idx is not None:
        # Find "Dest. Subnet Traffic Rate - Peak"
        peak_idx = None
        for i in range(traffic_rate_idx + 1, len(lines)):
            if lines[i].startswith('Dest. Subnet Traffic Rate - Peak'):
                peak_idx = i
                break

        # Parse Peak line
        if peak_idx is not None and peak_idx + 1 < len(lines):
            peak_line = re.sub(r'^[| ]+', '', lines[peak_idx + 1]) # Remove leading junk
            m = re.match(r'[\d\.\/]+\s+([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', peak_line, re.IGNORECASE)
            if m:
                raw_peak_rate = m.group(1).replace(' ', '')
                result['Peak Traffic Rate (in Kbps)'] = convert_to_kbps(raw_peak_rate)
                result['Peak Traffic Time'] = m.group(2)

        # Parse Average line
        start_avg_scan = peak_idx + 2 if peak_idx is not None else traffic_rate_idx + 1
        for i in range(start_avg_scan, len(lines)):
            avg_line = re.sub(r'^[| ]+', '', lines[i]) # Remove leading junk
            m = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line, re.IGNORECASE)
            if m:
                raw_avg_rate = m.group(1).replace(' ', '')
                result['Average Traffic (kbps)'] = convert_to_kbps(raw_avg_rate)
                result['Average Data'] = m.group(2)
                break
            # Handle case where "Average" is on its own line
            if avg_line.lower() == "average" and i + 1 < len(lines):
                avg_line2 = re.sub(r'^[| ]+', '', lines[i + 1])
                m2 = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line2, re.IGNORECASE)
                if m2:
                    raw_avg_rate = m2.group(1).replace(' ', '')
                    result['Average Traffic (kbps)'] = convert_to_kbps(raw_avg_rate)
                    result['Average Data'] = m2.group(2)
                    break

    # Final cleanup for Average Data
    if result.get('Average Data', '').startswith('(') and result.get('Average Data', '').endswith(')'):
        result['Average Data'] = result['Average Data'][1:-1]

    # Fill any remaining empty keys with "Not Available" for consistency
    for key in ALL_KEYS:
        if not result.get(key):
            result[key] = ""

    return result

# def parse_ocr_result(text):
#     """
#     Parses OCR text from a network report.

#     If the text is invalid (missing the 'Destination Networks' marker),
#     it returns a dictionary with all values set to 'Not Available'
#     instead of raising an error.

#     MODIFICATION: Traffic rates are converted to Kbps and their keys are renamed.
#     """
#     # Define all possible keys for the output dictionary. This makes it easy to
#     # create a consistent "Not Available" response.
#     # MODIFICATION: Renamed traffic rate keys.
#     ALL_KEYS = [
#         'Title', 'Time Range', 'Source Device', 'Source Device IP',
#         'In Interface', 'Description', 'Speed', 'Dest Subnet', 'Dest Mask',
#         'Peak Traffic Rate (in Kbps)', 'Peak Traffic Time', 'Average Traffic (kbps)', 'Average Data'
#     ]

#     # Clean up input lines
#     lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

#     # If the input is empty after stripping, it's invalid.
#     if not lines:
#         return {key: "Not Available" for key in ALL_KEYS}

#     # Find the index of the "Destination Networks" line.
#     # If it's not found, we consider the file invalid and return a "Not Available" dict.
#     try:
#         dest_net_idx = lines.index('Destination Networks')
#     except ValueError:
#         # Instead of raising an error, return a dictionary
#         # indicating that the data is not available for this input.
#         return {key: "Not Available" for key in ALL_KEYS}

#     # Initialize the result dictionary with empty strings for all keys.
#     # This is cleaner than adding them one by one.
#     result = {key: '' for key in ALL_KEYS}

#     # --- Start Parsing ---

#     # Parse Title
#     title = ' - '.join(lines[:dest_net_idx])
#     result['Title'] = title

#     # Find the 'Traffic Rate' section index (it's optional)
#     try:
#         traffic_rate_idx = lines.index('Traffic Rate')
#     except ValueError:
#         traffic_rate_idx = None

#     # Parse fields between "Destination Networks" and "Traffic Rate"
#     field_patterns = {
#         'Time Range':      r'Time range:\s*(.*)',
#         'Source Device':   r'Source device:\s*([^\s]+)\s*\(([^)]+)\)',
#         'In Interface':    r'In interface:\s*(.*)',
#         'Description':     r'Description:\s*(.*)',
#         'Speed':           r'Speed:\s*(.*)',
#         'Dest Subnet':     r'Dest subnet:\s*(.*)',
#         'Dest Mask':       r'Dest mask:\s*(.*)',
#     }

#     scan_end = traffic_rate_idx if traffic_rate_idx is not None else len(lines)
#     for line in lines[dest_net_idx+1:scan_end]:
#         for key, pattern in field_patterns.items():
#             m = re.match(pattern, line)
#             if m:
#                 if key == 'Source Device':
#                     result['Source Device'] = m.group(1)
#                     result['Source Device IP'] = m.group(2)
#                 else:
#                     result[key] = m.group(1)
#                 break # Move to the next line once a pattern is matched

#     # Parse the "Traffic Rate" section if it exists
#     if traffic_rate_idx is not None:
#         # Find "Dest. Subnet Traffic Rate - Peak"
#         peak_idx = None
#         for i in range(traffic_rate_idx + 1, len(lines)):
#             if lines[i].startswith('Dest. Subnet Traffic Rate - Peak'):
#                 peak_idx = i
#                 break

#         # Parse Peak line
#         if peak_idx is not None and peak_idx + 1 < len(lines):
#             peak_line = re.sub(r'^[| ]+', '', lines[peak_idx + 1]) # Remove leading junk
#             m = re.match(r'[\d\.\/]+\s+([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', peak_line, re.IGNORECASE)
#             if m:
#                 # MODIFICATION: Convert rate to Kbps and store under the new key
#                 raw_peak_rate = m.group(1).replace(' ', '')
#                 result['Peak Traffic Rate (in Kbps)'] = convert_to_kbps(raw_peak_rate)
#                 result['Peak Traffic Time'] = m.group(2)

#         # Parse Average line
#         start_avg_scan = peak_idx + 2 if peak_idx is not None else traffic_rate_idx + 1
#         for i in range(start_avg_scan, len(lines)):
#             avg_line = re.sub(r'^[| ]+', '', lines[i]) # Remove leading junk
#             m = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line, re.IGNORECASE)
#             if m:
#                 # MODIFICATION: Convert rate to Kbps and store under the new key
#                 raw_avg_rate = m.group(1).replace(' ', '')
#                 result['Average Traffic (kbps)'] = convert_to_kbps(raw_avg_rate)
#                 result['Average Data'] = m.group(2)
#                 break
#             # Handle case where "Average" is on its own line
#             if avg_line.lower() == "average" and i + 1 < len(lines):
#                 avg_line2 = re.sub(r'^[| ]+', '', lines[i + 1])
#                 m2 = re.match(r'([\d\.]+\s*[kMGT]?bps)\s*\((.+)\)', avg_line2, re.IGNORECASE)
#                 if m2:
#                     # MODIFICATION: Convert rate to Kbps and store under the new key
#                     raw_avg_rate = m2.group(1).replace(' ', '')
#                     result['Average Traffic (kbps)'] = convert_to_kbps(raw_avg_rate)
#                     result['Average Data'] = m2.group(2)
#                     break

#     # Final cleanup for Average Data
#     if result['Average Data'].startswith('(') and result['Average Data'].endswith(')'):
#         result['Average Data'] = result['Average Data'][1:-1]

#     return result