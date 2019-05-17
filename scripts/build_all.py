# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import argparse
import os
import subprocess

ARCHES = ['cpu', 'gpu']
VERSION = '1.13.1'
REPO = 'sagemaker-tensorflow-scriptmode'
PY2_CPU_BINARY = 'https://s3-us-west-2.amazonaws.com/tensorflow-aws/1.13/AmazonLinux/cpu/latest-patch-latest-patch/tensorflow-1.13.1-cp27-cp27mu-linux_x86_64.whl'
PY3_CPU_BINARY = 'https://s3-us-west-2.amazonaws.com/tensorflow-aws/1.13/AmazonLinux/cpu/latest-patch-latest-patch/tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl'
PY2_GPU_BINARY = 'https://s3-us-west-2.amazonaws.com/tensorflow-aws/1.13/AmazonLinux/gpu/latest-patch-latest-patch/tensorflow-1.13.1-cp27-cp27mu-linux_x86_64.whl'
PY3_GPU_BINARY = 'https://s3-us-west-2.amazonaws.com/tensorflow-aws/1.13/AmazonLinux/gpu/latest-patch-latest-patch/tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl'


def _parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--version', type=str, default=VERSION)
    parser.add_argument('--py2-cpu-binary', type=str, default=PY2_CPU_BINARY)
    parser.add_argument('--py3-cpu-binary', type=str, default=PY3_CPU_BINARY)
    parser.add_argument('--py2-gpu-binary', type=str, default=PY2_GPU_BINARY)
    parser.add_argument('--py3-gpu-binary', type=str, default=PY3_GPU_BINARY)
    parser.add_argument('--repo', type=str, default=REPO)

    return parser.parse_args()


args = _parse_args()
binaries = {
    'py2-cpu': args.py2_cpu_binary,
    'py3-cpu': args.py3_cpu_binary,
    'py2-gpu': args.py2_gpu_binary,
    'py3-gpu': args.py3_gpu_binary
}
build_dir = 'docker/{}'.format(args.version)

for arch in ['gpu']:
    for py_version in ['2', '3']:
        binary_url = binaries['py{}-{}'.format(py_version, arch)]
        binary_file = os.path.basename(binary_url)
        cmd = 'wget -O {}/{} {}'.format(build_dir, binary_file, binary_url)
        print(cmd)
        subprocess.check_call(cmd.split())
        tag = '{}-{}-py{}'.format(args.version, arch, py_version)
        build_cmd = 'docker build -f {}/Dockerfile.{} --build-arg py_version={} --build-arg framework_installable={} ' \
                    '-t {}:{} {}'.format(build_dir, arch, py_version, binary_file, args.repo, tag, build_dir)
        print(build_cmd)
        subprocess.check_call(build_cmd.split())
        print('Deleting binary file')
        subprocess.check_call('rm {}/{}'.format(build_dir, binary_file).split())
