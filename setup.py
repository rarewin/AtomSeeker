from setuptools import setup, find_packages

setup(
    name='AtomSeeker',
    version='0.0.1',
    description='Analyzer for MP4/MOV format file',
    packages=find_packages(),
    author='Katsuki Kobayashi',
    author_email='rare@tirasweel.org',
    license='BSD 2-Clause License',
    entry_points="""
        [console_scripts]
        atomseek = atomseeker.cmdline:main
    """,
    test_suite="tests",
    setup_requires=["pytest-runner", ],
    tests_require=["pytest", ],
)
