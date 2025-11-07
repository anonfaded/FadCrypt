# File Generator Script
# Configuration: List of file sizes in MB to generate
FILE_SIZES_MB = [100, 250, 500]

import os
import time
from colorama import init, Fore, Back, Style
import sys

# Initialize colorama
init(autoreset=True)

def generate_file(size_mb, filename):
    """Generate a file of specified size in MB with random data."""
    size_bytes = size_mb * 1024 * 1024
    start_time = time.time()
    
    spinner = ['|', '/', '-', '\\']
    spinner_idx = 0
    
    with open(filename, 'wb') as f:
        bytes_written = 0
        while bytes_written < size_bytes:
            chunk_size = min(1024 * 1024, size_bytes - bytes_written)  # 1MB chunks
            data = os.urandom(chunk_size)  # Use os.urandom for faster random data generation
            f.write(data)
            bytes_written += chunk_size
            
            # Update progress every 10MB for better performance
            if bytes_written % (10 * 1024 * 1024) == 0 or bytes_written == size_bytes:
                progress = (bytes_written / size_bytes) * 100
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed = bytes_written / elapsed / (1024 * 1024)  # MB/s
                    eta = (size_bytes - bytes_written) / (speed * 1024 * 1024) if speed > 0 else 0
                else:
                    eta = 0
                
                # Spinner animation
                display_name = os.path.basename(filename)
                progress_msg = f'{spinner[spinner_idx]} Generating {display_name}: {progress:.1f}% | Speed: {speed:.2f} MB/s | ETA: {eta:.1f}s'
                # Pad to fixed width to overwrite properly
                progress_msg = progress_msg.ljust(80)
                sys.stdout.write(f'\r{Fore.CYAN}{progress_msg}{Style.RESET_ALL}')
                sys.stdout.flush()
                spinner_idx = (spinner_idx + 1) % len(spinner)
    
    # Clear the progress line
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    return time.time() - start_time

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    total_start_time = time.time()
    
    print(f"{Fore.GREEN}Starting file generation...{Style.RESET_ALL}")
    
    generated_files = []
    for size in FILE_SIZES_MB:
        filename = f"test_{size}MB.bin"
        filepath = os.path.join(script_dir, filename)
        
        generation_time = generate_file(size, filepath)
        
        actual_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        generated_files.append(f"{filename} ({actual_size:.1f}MB in {generation_time:.2f}s)")
    
    total_time = time.time() - total_start_time
    print(f"{Fore.BLUE}✓ All files generated successfully in {total_time:.2f}s:{Style.RESET_ALL}")
    for file_info in generated_files:
        print(f"  {Fore.CYAN}• {file_info}{Style.RESET_ALL}")