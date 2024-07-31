"""This generates a Visual Studio solution file and projects for each module."""

from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from enum import Enum
import amulet_nbt
import pybind11
from binascii import hexlify
import sys
import glob
import sysconfig

SrcDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")

ProjectPattern = re.compile(
    r'Project\("{(?P<sln_guid>[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})}"\) = "(?P<project_name>[a-zA-Z0-9_-]+)", "(?P<proj_path>[a-zA-Z0-9\\/_-]+\.vcxproj)", "{(?P<project_guid>[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})}"'
)

PythonExtensionModuleSuffix = (
    f".cp{sys.version_info.major}{sys.version_info.minor}-win_amd64.pyd"
)

PythonIncludeDir = sysconfig.get_paths()["include"]
PythonLibraryDir = os.path.join(os.path.dirname(PythonIncludeDir), "libs")


VCXProjSource = """\
    <ClCompile Include="{path}" />"""
VCXProjInclude = """\
    <ClInclude Include="{path}" />"""

VCXProj = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <VCProjectVersion>17.0</VCProjectVersion>
    <ProjectGuid>{{{project_guid}}}</ProjectGuid>
    <Keyword>Win32Proj</Keyword>
    <WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>{library_type}</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v143</PlatformToolset>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="Configuration">
    <ConfigurationType>{library_type}</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v143</PlatformToolset>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="Shared">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <IntDir>$(SolutionDir)$(Platform)\$(Configuration)\int\{project_name}\</IntDir>
    <OutDir>{out_dir}</OutDir>
    <TargetExt>{file_extension}</TargetExt>
    <LibraryPath>$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);{library_path}</LibraryPath>
    <TargetName>{ext_name}</TargetName>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <IntDir>$(SolutionDir)$(Platform)\$(Configuration)\int\{project_name}\</IntDir>
    <OutDir>{out_dir}</OutDir>
    <TargetExt>{file_extension}</TargetExt>
    <LibraryPath>$(VC_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);$(WindowsSDK_LibraryPath_x64);{library_path}</LibraryPath>
    <TargetName>{ext_name}</TargetName>
  </PropertyGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <ClCompile>
      <LanguageStandard>stdcpp20</LanguageStandard>
      <AdditionalIncludeDirectories>{include_dirs}%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>
    </ClCompile>
    <Link>
      <AdditionalDependencies>$(CoreLibraryDependencies);%(AdditionalDependencies);{libraries}</AdditionalDependencies>
    </Link>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <ClCompile>
      <LanguageStandard>stdcpp20</LanguageStandard>
      <AdditionalIncludeDirectories>{include_dirs}%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>
    </ClCompile>
    <Link>
      <AdditionalDependencies>$(CoreLibraryDependencies);%(AdditionalDependencies);{libraries}</AdditionalDependencies>
    </Link>
  </ItemDefinitionGroup>
  <ItemGroup>
{source_files}
  </ItemGroup>
  <ItemGroup>
{include_files}
  </ItemGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>"""


VCXProjFiltersSource = """\
    <ClCompile Include="{path}">
      <Filter>Source Files</Filter>
    </ClCompile>"""


VCXProjFiltersInclude = """\
    <ClInclude Include="{path}">
      <Filter>Header Files</Filter>
    </ClInclude>"""


VCXProjFilters = r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Filter Include="Source Files">
      <UniqueIdentifier>{{4FC737F1-C7A5-4376-A066-2A32D752A2FF}}</UniqueIdentifier>
      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx</Extensions>
    </Filter>
    <Filter Include="Header Files">
      <UniqueIdentifier>{{93995380-89BD-4b04-88EB-625FBE52EBFB}}</UniqueIdentifier>
      <Extensions>h;hh;hpp;hxx;hm;inl;inc;xsd</Extensions>
    </Filter>
    <Filter Include="Resource Files">
      <UniqueIdentifier>{{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}}</UniqueIdentifier>
      <Extensions>rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx;tiff;tif;png;wav</Extensions>
    </Filter>
  </ItemGroup>
  <ItemGroup>
{source_files}
  </ItemGroup>
  <ItemGroup>
{include_files}
  </ItemGroup>
</Project>"""


VCXProjUser = r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="Current" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup />
</Project>"""


SolutionHeader = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.2.32630.192
MinimumVisualStudioVersion = 10.0.40219.1
"""

SolutionProjectDependency = """\
		{{{dependency_guid}}} = {{{dependency_guid}}}
"""
SolutionProjectDependencies = """\
	ProjectSection(ProjectDependencies) = postProject
{project_dependencies}\
	EndProjectSection
"""

SolutionProject = """Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{project_name}", "{project_name}.vcxproj", "{{{project_guid}}}"
{project_dependencies}EndProject
"""

SolutionGlobalConfigurationPlatforms = """\
		{{{project_guid}}}.Debug|x64.ActiveCfg = Debug|x64
		{{{project_guid}}}.Debug|x64.Build.0 = Debug|x64
		{{{project_guid}}}.Debug|x86.ActiveCfg = Debug|x64
		{{{project_guid}}}.Debug|x86.Build.0 = Debug|x64
		{{{project_guid}}}.Release|x64.ActiveCfg = Release|x64
		{{{project_guid}}}.Release|x64.Build.0 = Release|x64
		{{{project_guid}}}.Release|x86.ActiveCfg = Release|x64
		{{{project_guid}}}.Release|x86.Build.0 = Release|x64"""


SolutionGlobal = """\
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|x64 = Debug|x64
		Debug|x86 = Debug|x86
		Release|x64 = Release|x64
		Release|x86 = Release|x86
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
{configuration_platforms}
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
	GlobalSection(ExtensibilityGlobals) = postSolution
		SolutionGuid = {{6B72B1FC-8248-4021-B089-D05ED8CBCE73}}
	EndGlobalSection
EndGlobal
"""


class CompileMode(Enum):
    HeaderLibrary = "HeaderLibrary"
    DynamicLibrary = "DynamicLibrary"
    StaticLibrary = "StaticLibrary"
    PythonExtension = "pyd"


@dataclass(kw_only=True)
class ProjectData:
    name: str
    compile_mode: CompileMode
    source_files: list[str] = field(default_factory=list)
    include_files: list[str] = field(default_factory=list)
    include_dirs: list[str] = field(default_factory=list)
    library_dirs: list[str] = field(default_factory=list)
    dependencies: list[ProjectData] = field(default_factory=list)
    py_package: str | None = None

    def project_guid(self) -> str:
        encoded_name = self.name.encode()
        if len(encoded_name) > 16:
            raise Exception("Name too long. Fix this.")
        encoded_name = b"\x00" * (16 - len(encoded_name)) + encoded_name
        return (
            hexlify(encoded_name[0:4]).decode().upper()
            + "-"
            + hexlify(encoded_name[4:6]).decode().upper()
            + "-"
            + hexlify(encoded_name[6:8]).decode().upper()
            + "-"
            + hexlify(encoded_name[8:10]).decode().upper()
            + "-"
            + hexlify(encoded_name[10:16]).decode().upper()
        )


def write(
    src_dir: str, solution_dir: str, solution_name: str, projects: list[ProjectData]
) -> None:
    os.makedirs(solution_dir, exist_ok=True)
    for project in projects:
        project_guid = project.project_guid()
        vcxproj_sources = "\n".join(
            VCXProjSource.format(path=path) for path in project.source_files
        )
        vcxproj_includes = "\n".join(
            VCXProjInclude.format(path=path) for path in project.include_files
        )
        library_type = project.compile_mode
        project_name = project.name
        if library_type == CompileMode.PythonExtension:
            extension = PythonExtensionModuleSuffix
            library_type = CompileMode.DynamicLibrary
            if project.py_package:
                module_path = project.py_package.replace(".", "\\")
                out_dir = f"{src_dir}\\{module_path}\\"
                project_name = f"{project.py_package}.{project_name}"
            else:
                out_dir = f"{src_dir}\\"
        elif library_type == CompileMode.StaticLibrary or library_type == CompileMode.DynamicLibrary.HeaderLibrary:
            extension = ".lib"
            out_dir = f"$(SolutionDir)$(Platform)\\$(Configuration)\\out\\{project.name}\\"
        # elif library_type == CompileMode.DynamicLibrary:
        #     extension = ".dll"
        #     out_dir = f"$(SolutionDir)$(Platform)\\$(Configuration)\\out\\{project.name}\\"
        else:
            raise RuntimeError
        with open(
            os.path.join(solution_dir, f"{project_name}.vcxproj"), "w", encoding="utf8"
        ) as f:
            f.write(
                VCXProj.format(
                    project_name=project_name,
                    ext_name=project.name,
                    source_files=vcxproj_sources,
                    include_files=vcxproj_includes,
                    include_dirs="".join(f"{path};" for path in project.include_dirs),
                    library_path="".join(
                        [f"{path};" for path in project.library_dirs]
                        + [
                            f"$(SolutionDir)$(Platform)\\$(Configuration)\\out\\{dep.name}\\;"
                            for dep in project.dependencies
                            if dep.compile_mode == CompileMode.StaticLibrary
                        ]
                    ),
                    libraries="".join(
                        f"{dep.name}.lib;" for dep in project.dependencies if dep.compile_mode == CompileMode.StaticLibrary
                    ),
                    library_type=library_type.value,
                    project_guid=project_guid,
                    file_extension=extension,
                    out_dir=out_dir,
                )
            )
        filter_sources = "\n".join(
            VCXProjFiltersSource.format(path=path) for path in project.source_files
        )
        filter_includes = "\n".join(
            VCXProjFiltersInclude.format(path=path) for path in project.include_files
        )
        with open(
            os.path.join(solution_dir, f"{project_name}.vcxproj.filters"),
            "w",
            encoding="utf8",
        ) as f:
            f.write(
                VCXProjFilters.format(
                    source_files=filter_sources, include_files=filter_includes
                )
            )
        with open(
            os.path.join(solution_dir, f"{project_name}.vcxproj.user"),
            "w",
            encoding="utf8",
        ) as f:
            f.write(VCXProjUser)

    # write solution file
    with open(
        os.path.join(solution_dir, f"{solution_name}.sln"), "w", encoding="utf8"
    ) as f:
        f.write(SolutionHeader)
        global_configuration_platforms = []
        for project in projects:
            project_guid = project.project_guid()
            project_name = f"{project.py_package}.{project.name}" if project.py_package else project.name
            if project.dependencies:
                project_dependencies = "".join(
                    SolutionProjectDependency.format(dependency_guid=dep.project_guid())
                    for dep in project.dependencies
                )
                project_dependencies = SolutionProjectDependencies.format(
                    project_dependencies=project_dependencies
                )
            else:
                project_dependencies = ""
            f.write(
                SolutionProject.format(
                    project_name=project_name,
                    project_guid=project_guid,
                    project_dependencies=project_dependencies,
                )
            )
            global_configuration_platforms.append(
                SolutionGlobalConfigurationPlatforms.format(project_guid=project_guid)
            )
        f.write(
            SolutionGlobal.format(
                configuration_platforms="\n".join(global_configuration_platforms)
            )
        )


def main() -> None:
    amulet_nbt_project = ProjectData(
        name="amulet_nbt",
        compile_mode=CompileMode.StaticLibrary,
        source_files=glob.glob(
            os.path.join(glob.escape(amulet_nbt.get_source()), "**", "*.cpp"),
            recursive=True,
        ),
        include_files=glob.glob(
            os.path.join(glob.escape(amulet_nbt.get_include()), "**", "*.hpp"),
            recursive=True,
        ),
        include_dirs=[amulet_nbt.get_include()],
    )
    amulet_project = ProjectData(
        name="amulet_core",
        compile_mode=CompileMode.StaticLibrary,
        source_files=glob.glob(
            os.path.join(glob.escape(SrcDir), "amulet", "cpp", "**", "*.cpp"),
            recursive=True,
        ),
        include_files=glob.glob(
            os.path.join(glob.escape(SrcDir), "amulet", "cpp", "**", "*.hpp"),
            recursive=True,
        ),
        include_dirs=[amulet_nbt.get_include(), os.path.join(SrcDir, "amulet", "cpp")],
        dependencies=[amulet_nbt_project],
    )
    projects = [
        amulet_nbt_project,
        amulet_project,
    ]

    for cpp_path in glob.glob(
        os.path.join(glob.escape(SrcDir), "**", "*.cpp"), recursive=True
    ):
        with open(cpp_path) as f:
            src = f.read()
            match = re.search(r"PYBIND11_MODULE\((?P<module>[a-zA-Z0-9]+), m\)", src)
            if match:
                module_name = match.group("module")
                assert (
                    os.path.splitext(os.path.basename(cpp_path))[0] == module_name
                ), f"module name must match file name. {cpp_path}"
                package = os.path.relpath(os.path.dirname(cpp_path), SrcDir).replace(
                    os.sep, "."
                )
                projects.append(
                    ProjectData(
                        name=module_name,
                        compile_mode=CompileMode.PythonExtension,
                        source_files=[cpp_path],
                        include_dirs=[
                            PythonIncludeDir,
                            pybind11.get_include(),
                            amulet_nbt.get_include(),
                            os.path.join(SrcDir, "amulet", "cpp"),
                        ],
                        library_dirs=[
                            PythonLibraryDir,
                        ],
                        py_package=package,
                        dependencies=[amulet_nbt_project, amulet_project],
                    )
                )

    write(
        SrcDir,
        os.path.join(SrcDir, "sln"),
        "Amulet-Core",
        projects,
    )


if __name__ == "__main__":
    main()
