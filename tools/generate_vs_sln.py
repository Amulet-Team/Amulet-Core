"""This generates a Visual Studio solution file and projects for each module."""

from __future__ import annotations
import os
import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
import amulet_nbt
import pybind11
from binascii import hexlify
import sys
import glob
import sysconfig
from collections.abc import Iterable

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
      <Filter>{rel_path}</Filter>
    </ClCompile>"""


VCXProjFiltersSourceGroup = """\
    <Filter Include="{path}">
      <UniqueIdentifier>{{{uuid}}}</UniqueIdentifier>
    </Filter>
"""


VCXProjFiltersInclude = """\
    <ClInclude Include="{path}">
      <Filter>{rel_path}</Filter>
    </ClInclude>"""


VCXProjFiltersIncludeGroup = """\
    <Filter Include="{path}">
      <UniqueIdentifier>{{{uuid}}}</UniqueIdentifier>
    </Filter>
"""


VCXProjFilters = r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
{filter_groups}  </ItemGroup>
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
    DynamicLibrary = "DynamicLibrary"
    StaticLibrary = "StaticLibrary"
    PythonExtension = "pyd"


@dataclass(kw_only=True)
class ProjectData:
    name: str
    compile_mode: CompileMode
    source_files: list[tuple[str, str, str]] = field(default_factory=list)
    include_files: list[tuple[str, str, str]] = field(default_factory=list)
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
            VCXProjSource.format(path=os.path.join(*path))
            for path in project.source_files
        )
        vcxproj_includes = "\n".join(
            VCXProjInclude.format(path=os.path.join(*path))
            for path in project.include_files
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
        elif library_type == CompileMode.StaticLibrary:
            extension = ".lib"
            out_dir = (
                f"$(SolutionDir)$(Platform)\\$(Configuration)\\out\\{project.name}\\"
            )
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
                            and dep.source_files
                        ]
                    ),
                    libraries="".join(
                        f"{dep.name}.lib;"
                        for dep in project.dependencies
                        if dep.compile_mode == CompileMode.StaticLibrary
                        and dep.source_files
                    ),
                    library_type=library_type.value,
                    project_guid=project_guid,
                    file_extension=extension,
                    out_dir=out_dir,
                )
            )
        filter_sources = []
        filter_includes = []
        filter_sources_groups = dict[str, str]()
        filter_includes_groups = dict[str, str]()
        for path in project.source_files:
            filter_sources.append(
                VCXProjFiltersSource.format(
                    path=os.path.join(*path), rel_path=path[1] or ""
                )
            )
            rel_path = path[1]
            while rel_path:
                if rel_path not in filter_sources_groups:
                    filter_sources_groups[rel_path] = VCXProjFiltersSourceGroup.format(
                        path=rel_path, uuid=str(uuid.uuid4())
                    )
                rel_path = os.path.dirname(rel_path)
        for path in project.include_files:
            filter_includes.append(
                VCXProjFiltersInclude.format(
                    path=os.path.join(*path), rel_path=path[1] or ""
                )
            )
            rel_path = path[1]
            while rel_path:
                if rel_path not in filter_includes_groups:
                    filter_includes_groups[rel_path] = (
                        VCXProjFiltersIncludeGroup.format(
                            path=rel_path, uuid=str(uuid.uuid4())
                        )
                    )
                rel_path = os.path.dirname(rel_path)
        with open(
            os.path.join(solution_dir, f"{project_name}.vcxproj.filters"),
            "w",
            encoding="utf8",
        ) as f:
            f.write(
                VCXProjFilters.format(
                    source_files="\n".join(filter_sources),
                    include_files="\n".join(filter_includes),
                    filter_groups="".join(filter_sources_groups.values())
                    + "".join(filter_includes_groups.values()),
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
            project_name = (
                f"{project.py_package}.{project.name}"
                if project.py_package
                else project.name
            )
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


def get_files(
    *,
    root_dir: str,
    ext: str,
    root_dir_suffix: str = "",
    exclude_dirs: Iterable[str] = (),
) -> list[tuple[str, str, str]]:
    """
    Get file paths split into
    1) containing folder ("your/path")
    2) relative path to parent directory within containing folder ("amulet/io")
    3) file name. ("binary_reader.hpp")
    get_files("your/path", "hpp")
    """
    paths = list[tuple[str, str, str]]()
    search_path = root_dir
    if root_dir_suffix:
        search_path = os.path.join(search_path, root_dir_suffix)
    for path in glob.iglob(
        os.path.join(glob.escape(search_path), "**", f"*.{ext}"), recursive=True
    ):
        if any(path.startswith(d) for d in exclude_dirs):
            continue
        rel_path = os.path.relpath(path, root_dir)
        paths.append((root_dir, os.path.dirname(rel_path), os.path.basename(rel_path)))
    return paths


def main() -> None:
    amulet_nbt_project = ProjectData(
        name="amulet_nbt",
        compile_mode=CompileMode.StaticLibrary,
        include_files=get_files(root_dir=amulet_nbt.get_include(), ext="hpp"),
        source_files=get_files(root_dir=amulet_nbt.get_source(), ext="cpp"),
        include_dirs=[amulet_nbt.get_include()],
    )
    amulet_py_project = ProjectData(
        name="__init__",
        compile_mode=CompileMode.PythonExtension,
        include_files=get_files(root_dir=SrcDir, ext="hpp", root_dir_suffix="amulet"),
        source_files=get_files(
            root_dir=SrcDir,
            ext="cpp",
            root_dir_suffix="amulet",
        ),
        include_dirs=[
            PythonIncludeDir,
            pybind11.get_include(),
            amulet_nbt.get_include(),
            SrcDir,
        ],
        library_dirs=[
            PythonLibraryDir,
        ],
        dependencies=[
            amulet_nbt_project,
        ],
        py_package="amulet",
    )
    projects = [
        amulet_nbt_project,
        amulet_py_project,
    ]

    write(
        SrcDir,
        os.path.join(SrcDir, "sln"),
        "Amulet-Core",
        projects,
    )


if __name__ == "__main__":
    main()
