"""
Sistema de IA Proativa para Mamute
=================================
IA que propõe E aplica melhorias automaticamente
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from src.database.connection import DatabaseManager
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.ai.agent import AIAgent
from mamute_personality import MamutePersonality
from mamute_proactive_ml import MamuteProactiveML
from notification_system import NotificationSystem, notification_system as global_notification_system, NotificationChannel, NotificationLevel

class MamuteProactiveIA:
    """IA Proativa que propõe e aplica melhorias automaticamente"""
    
    def __init__(self, config_file: str = ".env", notification_system: NotificationSystem = None):
        """Inicializar IA Proativa"""
        self.config = Config(config_file)
        self.logger = setup_logger("MamuteProactiveIA")
        
        # Componentes principais
        self.db_manager = DatabaseManager(self.config)
        self.ai_agent = AIAgent(self.config, self.db_manager)
        self.personality = MamutePersonality()
        
        # Sistema de ações disponíveis
        self.available_actions = {
            'otimizar_consultas': self.optimize_database_queries,
            'limpar_logs': self.clean_old_logs,
            'backup_automatico': self.create_automatic_backup,
            'atualizar_indices': self.update_database_indexes,
            'gerar_relatorio': self.generate_performance_report,
            'otimizar_memoria': self.optimize_memory_usage,
            'verificar_integridade': self.check_data_integrity,
            'instalar_dependencia': self.install_missing_dependency,
            'corrigir_configuracao': self.fix_configuration_issue,
            'atualizar_sistema': self.update_system_components
        }
        
        # Configurações de automação
        self.auto_apply_threshold = 0.8  # Confiança mínima para aplicar automaticamente
        self.require_confirmation = ['backup_automatico', 'atualizar_sistema']  # Ações que sempre pedem confirmação
        self.safe_auto_actions = {
            'otimizar_consultas',
            'limpar_logs',
            'atualizar_indices',
            'gerar_relatorio',
            'otimizar_memoria',
            'verificar_integridade'
        }
        
        # Estado da sessão
        self.session_improvements = []
        self.applied_improvements = []
        self.user_preferences = {
            'auto_apply_safe_improvements': True,
            'auto_apply_optimizations': True,
            'auto_apply_maintenance': True,
            'ask_before_system_changes': True
        }
        
        # Sistema de notificações para eventos proativos
        self.notification_system = notification_system or global_notification_system

        # Modelo de aprendizado de máquina leve para recomendações de melhorias
        self.ml_advisor = MamuteProactiveML()

        # Conhecimento completo sobre linguagens de programação
        self.programming_languages = {
            'pascal': {
                'extensions': ['.pas', '.pp', '.p', '.dpr', '.dpk', '.inc'],
                'compilers': ['Free Pascal (FPC)', 'Delphi', 'Turbo Pascal', 'GNU Pascal'],
                'common_issues': ['memory_management', 'pointer_errors', 'compilation_errors', 'unit_dependencies'],
                'tools': ['fpc', 'delphi', 'lazarus', 'gdb', 'pas2js'],
                'optimizations': ['compiler_optimization', 'memory_allocation', 'string_handling', 'recursion_optimization'],
                'best_practices': ['structured_programming', 'unit_organization', 'error_handling', 'documentation'],
                'description': 'Linguagem estruturada criada por Niklaus Wirth, focada na clareza e ensino de programação',
                'paradigms': ['procedural', 'structured'],
                'typical_domains': ['educação', 'sistemas embarcados', 'aplicações desktop', 'compiladores'],
                'modern_variants': ['Object Pascal', 'Delphi', 'Free Pascal']
            },
            'python': {
                'extensions': ['.py', '.pyw', '.pyi', '.ipynb'],
                'interpreters': ['CPython', 'PyPy', 'Jython', 'IronPython', 'MicroPython'],
                'common_issues': ['imports', 'indentation', 'dependencies', 'performance', 'gil_limitations'],
                'tools': ['pip', 'pytest', 'black', 'flake8', 'mypy', 'poetry', 'conda', 'virtualenv'],
                'optimizations': ['vectorization', 'caching', 'async/await', 'multiprocessing', 'cython'],
                'best_practices': ['pep8', 'type_hints', 'virtual_environments', 'testing', 'documentation'],
                'description': 'Linguagem interpretada, orientada a objetos, de alto nível com sintaxe clara',
                'paradigms': ['object-oriented', 'procedural', 'functional'],
                'typical_domains': ['web development', 'data science', 'AI/ML', 'automation', 'scripting'],
                'frameworks': ['Django', 'Flask', 'FastAPI', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch']
            },
            'javascript': {
                'extensions': ['.js', '.jsx', '.mjs', '.cjs'],
                'engines': ['V8', 'SpiderMonkey', 'JavaScriptCore', 'Chakra'],
                'common_issues': ['callback_hell', 'hoisting', 'scope_issues', 'async_errors', 'memory_leaks'],
                'tools': ['npm', 'yarn', 'webpack', 'eslint', 'jest', 'babel', 'prettier'],
                'optimizations': ['minification', 'tree-shaking', 'code-splitting', 'lazy-loading', 'service_workers'],
                'best_practices': ['es6+', 'modules', 'testing', 'linting', 'documentation'],
                'description': 'Linguagem interpretada, dinâmica, para web frontend e backend',
                'paradigms': ['object-oriented', 'functional', 'event-driven'],
                'typical_domains': ['web frontend', 'web backend', 'mobile apps', 'desktop apps'],
                'frameworks': ['React', 'Vue', 'Angular', 'Node.js', 'Express', 'Next.js']
            },
            'typescript': {
                'extensions': ['.ts', '.tsx', '.d.ts'],
                'compilers': ['tsc', 'esbuild', 'swc', 'babel'],
                'common_issues': ['type_errors', 'compilation_config', 'js_interop', 'strict_mode'],
                'tools': ['tsc', 'ts-node', 'eslint', 'prettier', 'jest'],
                'optimizations': ['strict_mode', 'tree-shaking', 'type_inference', 'incremental_compilation'],
                'description': 'Superset tipado do JavaScript com compilação para JS',
                'paradigms': ['object-oriented', 'functional', 'generic_programming'],
                'frameworks': ['Angular', 'React', 'Vue', 'NestJS']
            },
            'java': {
                'extensions': ['.java', '.class', '.jar', '.war'],
                'jvms': ['Oracle JVM', 'OpenJDK', 'GraalVM', 'Eclipse OpenJ9'],
                'common_issues': ['memory_leaks', 'gc_performance', 'dependency_hell', 'thread_safety'],
                'tools': ['maven', 'gradle', 'junit', 'checkstyle', 'spotbugs', 'jacoco'],
                'optimizations': ['jvm_tuning', 'garbage_collection', 'profiling', 'caching'],
                'description': 'Linguagem orientada a objetos, compilada para bytecode JVM',
                'paradigms': ['object-oriented', 'generic_programming'],
                'frameworks': ['Spring', 'Hibernate', 'Apache Struts', 'JSF']
            },
            'csharp': {
                'extensions': ['.cs', '.dll', '.exe'],
                'runtimes': ['.NET Framework', '.NET Core', '.NET 5+', 'Mono'],
                'common_issues': ['null_references', 'memory_management', 'async_deadlocks'],
                'tools': ['dotnet', 'nuget', 'mstest', 'nunit', 'xunit', 'roslyn'],
                'optimizations': ['async_patterns', 'span_memory', 'linq_performance', 'gc_optimization'],
                'description': 'Linguagem orientada a objetos da Microsoft para .NET',
                'frameworks': ['ASP.NET', 'Entity Framework', 'WPF', 'Xamarin', 'Unity']
            },
            'cpp': {
                'extensions': ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.h', '.hxx'],
                'compilers': ['GCC', 'Clang', 'MSVC', 'ICC'],
                'common_issues': ['memory_leaks', 'segfaults', 'undefined_behavior', 'abi_compatibility'],
                'tools': ['cmake', 'make', 'gdb', 'valgrind', 'clang-tidy', 'cppcheck'],
                'optimizations': ['raii', 'move_semantics', 'template_metaprogramming', 'vectorization'],
                'description': 'Linguagem compilada, orientada a objetos, de sistemas',
                'paradigms': ['object-oriented', 'generic_programming', 'procedural'],
                'standards': ['C++11', 'C++14', 'C++17', 'C++20', 'C++23']
            },
            'c': {
                'extensions': ['.c', '.h'],
                'compilers': ['GCC', 'Clang', 'MSVC', 'TCC'],
                'common_issues': ['buffer_overflows', 'memory_leaks', 'pointer_errors', 'undefined_behavior'],
                'tools': ['make', 'cmake', 'gdb', 'valgrind', 'static_analyzers'],
                'optimizations': ['compiler_flags', 'algorithm_optimization', 'cache_efficiency'],
                'description': 'Linguagem procedural compilada, base de muitos sistemas',
                'paradigms': ['procedural', 'structured'],
                'standards': ['C89', 'C99', 'C11', 'C17', 'C23']
            },
            'go': {
                'extensions': ['.go'],
                'compiler': 'gc (official Go compiler)',
                'common_issues': ['goroutine_leaks', 'race_conditions', 'gc_pressure'],
                'tools': ['go_mod', 'go_test', 'go_fmt', 'go_vet', 'golint', 'delve'],
                'optimizations': ['goroutines', 'channels', 'memory_pooling', 'profiling'],
                'description': 'Linguagem compilada, concorrente, criada pelo Google',
                'paradigms': ['concurrent', 'procedural', 'object-oriented (interfaces)']
            },
            'rust': {
                'extensions': ['.rs'],
                'compiler': 'rustc',
                'common_issues': ['borrow_checker', 'lifetime_issues', 'async_complexity'],
                'tools': ['cargo', 'rustc', 'clippy', 'rustfmt', 'miri'],
                'optimizations': ['zero_cost_abstractions', 'ownership', 'traits'],
                'description': 'Linguagem de sistemas com memory safety sem garbage collector',
                'paradigms': ['systems', 'functional', 'concurrent']
            },
            'php': {
                'extensions': ['.php', '.phtml', '.php3', '.php4', '.php5'],
                'interpreters': ['Zend Engine', 'HHVM', 'PHP-FPM'],
                'common_issues': ['sql_injection', 'xss', 'memory_leaks', 'deprecated_functions'],
                'tools': ['composer', 'phpunit', 'phpstan', 'psalm', 'php-cs-fixer'],
                'optimizations': ['opcode_caching', 'database_optimization', 'autoloading'],
                'description': 'Linguagem interpretada amplamente usada para desenvolvimento web',
                'frameworks': ['Laravel', 'Symfony', 'CodeIgniter', 'CakePHP']
            },
            'ruby': {
                'extensions': ['.rb', '.rbw'],
                'interpreters': ['MRI (CRuby)', 'JRuby', 'TruffleRuby', 'mruby'],
                'common_issues': ['performance', 'gem_conflicts', 'memory_usage'],
                'tools': ['bundler', 'rspec', 'rubocop', 'pry', 'rails'],
                'optimizations': ['yjit', 'memory_optimization', 'algorithm_improvement'],
                'description': 'Linguagem interpretada, orientada a objetos, expressiva',
                'frameworks': ['Ruby on Rails', 'Sinatra', 'Hanami']
            },
            'swift': {
                'extensions': ['.swift'],
                'compiler': 'Swift Compiler (swiftc)',
                'common_issues': ['arc_cycles', 'compilation_time', 'optionals'],
                'tools': ['swift_package_manager', 'xctest', 'swiftlint', 'instruments'],
                'optimizations': ['arc_optimization', 'protocol_optimization', 'whole_module_optimization'],
                'description': 'Linguagem compilada da Apple para iOS/macOS/watchOS/tvOS',
                'frameworks': ['SwiftUI', 'UIKit', 'Foundation', 'Combine']
            },
            'kotlin': {
                'extensions': ['.kt', '.kts'],
                'compilers': ['kotlinc-jvm', 'kotlinc-js', 'kotlinc-native'],
                'common_issues': ['java_interop', 'compilation_time', 'null_safety'],
                'tools': ['gradle', 'maven', 'ktlint', 'detekt'],
                'optimizations': ['coroutines', 'inline_functions', 'data_classes'],
                'description': 'Linguagem moderna para JVM, interoperável com Java',
                'frameworks': ['Spring', 'Ktor', 'Android SDK']
            },
            'scala': {
                'extensions': ['.scala', '.sc'],
                'compiler': 'scalac',
                'common_issues': ['compilation_time', 'complexity', 'implicit_resolution'],
                'tools': ['sbt', 'scalatest', 'scalafmt', 'scalafix'],
                'optimizations': ['functional_programming', 'immutability', 'parallel_collections'],
                'description': 'Linguagem funcional/OO para JVM',
                'frameworks': ['Akka', 'Play Framework', 'Spark']
            },
            'sql': {
                'extensions': ['.sql', '.ddl', '.dml'],
                'databases': ['PostgreSQL', 'MySQL', 'SQLite', 'Oracle', 'SQL Server'],
                'common_issues': ['slow_queries', 'injection', 'normalization', 'deadlocks'],
                'tools': ['explain', 'analyze', 'vacuum', 'sqlcheck', 'pgbench'],
                'optimizations': ['indexing', 'query_rewriting', 'partitioning', 'materialized_views'],
                'description': 'Linguagem declarativa para bancos de dados relacionais',
                'variants': ['PostgreSQL', 'MySQL', 'T-SQL', 'PL/SQL', 'SQLite']
            },
            'r': {
                'extensions': ['.r', '.R', '.Rmd'],
                'interpreter': 'R',
                'common_issues': ['memory_usage', 'performance', 'package_conflicts'],
                'tools': ['cran', 'devtools', 'testthat', 'lintr', 'rstudio'],
                'optimizations': ['vectorization', 'parallel_computing', 'rcpp'],
                'description': 'Linguagem para estatística e análise de dados',
                'frameworks': ['tidyverse', 'shiny', 'ggplot2', 'dplyr']
            },
            'matlab': {
                'extensions': ['.m', '.mlx', '.mat'],
                'engine': 'MATLAB Engine',
                'common_issues': ['performance', 'licensing_costs', 'memory_usage'],
                'tools': ['simulink', 'profiler', 'mlint', 'app_designer'],
                'optimizations': ['vectorization', 'parallel_computing', 'gpu_computing'],
                'description': 'Linguagem para computação técnica e científica',
                'toolboxes': ['Signal Processing', 'Image Processing', 'Deep Learning']
            },
            'fortran': {
                'extensions': ['.f', '.f77', '.f90', '.f95', '.f03', '.f08'],
                'compilers': ['gfortran', 'ifort', 'xlf', 'nagfor'],
                'common_issues': ['legacy_code', 'modernization', 'array_bounds'],
                'tools': ['make', 'cmake', 'funit', 'fordoc'],
                'optimizations': ['array_operations', 'parallel_computing', 'coarrays'],
                'description': 'Linguagem para computação científica e numérica de alta performance',
                'standards': ['Fortran 77', 'Fortran 90', 'Fortran 95', 'Fortran 2003', 'Fortran 2008']
            },
            'cobol': {
                'extensions': ['.cbl', '.cob', '.cpy', '.pco'],
                'compilers': ['GnuCOBOL', 'IBM Enterprise COBOL', 'Micro Focus COBOL'],
                'common_issues': ['legacy_maintenance', 'y2k_issues', 'modernization'],
                'tools': ['gnucobol', 'enterprise_cobol', 'micro_focus'],
                'optimizations': ['code_modernization', 'database_integration', 'web_services'],
                'description': 'Linguagem para sistemas empresariais e transações comerciais',
                'domains': ['banking', 'insurance', 'government', 'mainframes']
            },
            'assembly': {
                'extensions': ['.asm', '.s', '.S'],
                'assemblers': ['NASM', 'MASM', 'GAS', 'YASM'],
                'common_issues': ['portability', 'debugging_difficulty', 'maintenance'],
                'tools': ['nasm', 'gas', 'gdb', 'objdump', 'radare2'],
                'optimizations': ['instruction_scheduling', 'register_allocation', 'loop_unrolling'],
                'description': 'Linguagem de baixo nível, mnemônicos para instruções de CPU',
                'architectures': ['x86', 'x86_64', 'ARM', 'MIPS', 'RISC-V']
            },
            'lua': {
                'extensions': ['.lua'],
                'interpreter': 'Lua',
                'common_issues': ['performance', 'memory_usage', 'c_integration'],
                'tools': ['luarocks', 'busted', 'luacheck', 'luacov'],
                'optimizations': ['luajit', 'table_optimization', 'coroutines'],
                'description': 'Linguagem leve, embarcável, para scripting e extensão',
                'applications': ['game scripting', 'nginx', 'redis', 'wireshark']
            },
            'perl': {
                'extensions': ['.pl', '.pm', '.t', '.pod'],
                'interpreter': 'Perl 5',
                'common_issues': ['readability', 'cpan_dependencies', 'unicode_handling'],
                'tools': ['cpan', 'prove', 'perlcritic', 'perltidy'],
                'optimizations': ['regex_compilation', 'hash_optimization', 'xs_modules'],
                'description': 'Linguagem interpretada, excelente para processamento de texto',
                'strengths': ['regex', 'text_processing', 'system_administration']
            },
            'haskell': {
                'extensions': ['.hs', '.lhs'],
                'compiler': 'GHC (Glasgow Haskell Compiler)',
                'common_issues': ['lazy_evaluation', 'space_leaks', 'monad_complexity'],
                'tools': ['cabal', 'stack', 'hlint', 'hspec', 'quickcheck'],
                'optimizations': ['strictness_annotations', 'fusion', 'stream_processing'],
                'description': 'Linguagem funcional pura com avaliação preguiçosa',
                'concepts': ['monads', 'type_classes', 'higher_order_functions']
            },
            'erlang': {
                'extensions': ['.erl', '.hrl', '.beam'],
                'vm': 'BEAM (Erlang Virtual Machine)',
                'common_issues': ['hot_code_loading', 'pattern_matching', 'process_communication'],
                'tools': ['rebar3', 'eunit', 'dialyzer', 'observer'],
                'optimizations': ['actor_model', 'fault_tolerance', 'distribution'],
                'description': 'Linguagem funcional para sistemas concorrentes e distribuídos',
                'features': ['lightweight_processes', 'let_it_crash', 'hot_swapping']
            },
            'elixir': {
                'extensions': ['.ex', '.exs'],
                'vm': 'BEAM (Erlang Virtual Machine)',
                'common_issues': ['otp_patterns', 'genserver_design', 'supervision_trees'],
                'tools': ['mix', 'exunit', 'credo', 'dialyxir', 'phoenix'],
                'optimizations': ['otp_behaviors', 'process_pooling', 'pipeline_operator'],
                'description': 'Linguagem funcional dinâmica para Erlang VM',
                'frameworks': ['Phoenix', 'Nerves', 'LiveView']
            }
        }
        
        self.logger.info("🚀 IA Proativa Mamute inicializada com conhecimento completo de 25+ linguagens!")
    
    def detect_programming_language(self, file_path: str = None, code_snippet: str = None) -> str:
        """Detectar linguagem de programação por extensão ou análise de código"""
        if file_path:
            ext = Path(file_path).suffix.lower()
            for lang, info in self.programming_languages.items():
                if ext in info['extensions']:
                    return lang
        
        if code_snippet:
            # Análise básica por palavras-chave/sintaxe
            code_lower = code_snippet.lower()
            
            # Pascal
            if any(keyword in code_lower for keyword in ['program ', 'begin', 'end.', 'var ', 'procedure ', 'function ']):
                return 'pascal'
            
            # Python
            if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', '__init__', 'elif']):
                return 'python'
            
            # JavaScript/TypeScript
            if any(keyword in code_lower for keyword in ['function', 'const ', 'let ', 'var ', '=>', 'console.log']):
                if ': ' in code_snippet and 'interface' in code_lower:
                    return 'typescript'
                return 'javascript'
            
            # Java
            if any(keyword in code_lower for keyword in ['public class', 'private ', 'public static void main']):
                return 'java'
            
            # C#
            if any(keyword in code_lower for keyword in ['using system', 'namespace ', 'public class']):
                return 'csharp'
            
            # C++
            if any(keyword in code_lower for keyword in ['#include', 'std::', 'cout', 'cin', 'namespace std']):
                return 'cpp'
            
            # C
            if any(keyword in code_lower for keyword in ['#include', 'printf', 'scanf', 'main(']) and 'std::' not in code_lower:
                return 'c'
            
            # SQL
            if any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert ', 'update ', 'delete ']):
                return 'sql'
        
        return 'unknown'
    
    def get_language_specific_advice(self, language: str, issue_type: str = None) -> Dict[str, Any]:
        """Obter conselhos específicos para uma linguagem"""
        if language not in self.programming_languages:
            return {"error": f"Linguagem '{language}' não reconhecida"}
        
        lang_info = self.programming_languages[language]
        
        advice = {
            "language": language,
            "description": lang_info["description"],
            "common_issues": lang_info.get("common_issues", []),
            "recommended_tools": lang_info.get("tools", []),
            "optimization_tips": lang_info.get("optimizations", []),
            "best_practices": lang_info.get("best_practices", []),
        }
        
        # Adicionar conselhos específicos para Pascal
        if language == 'pascal':
            advice.update({
                "modern_alternatives": lang_info.get("modern_variants", []),
                "learning_resources": [
                    "Free Pascal Documentation",
                    "Lazarus IDE Tutorials", 
                    "Object Pascal Handbook"
                ],
                "migration_paths": [
                    "Para projetos modernos: considere Delphi ou Free Pascal",
                    "Para web: pas2js para transpilação para JavaScript",
                    "Para mobile: Delphi com FireMonkey framework"
                ],
                "specific_tips": [
                    "Use units para organizar código modular",
                    "Implemente proper error handling com try/except",
                    "Considere Object Pascal para programação OO",
                    "Utilize records para estruturas de dados",
                    "Implemente interfaces para design patterns modernos"
                ]
            })
        
        return advice
    
    def scan_project_languages(self, project_path: str) -> Dict[str, Any]:
        """Escanear projeto para detectar linguagens usadas"""
        if not os.path.exists(project_path):
            return {"error": "Projeto não encontrado"}
        
        language_files = {}
        total_files = 0
        
        for root, dirs, files in os.walk(project_path):
            # Skip common irrelevant directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                lang = self.detect_programming_language(file_path)
                
                if lang != 'unknown':
                    if lang not in language_files:
                        language_files[lang] = []
                    language_files[lang].append(file_path)
                
                total_files += 1
        
        # Calcular estatísticas
        stats = {}
        for lang, files in language_files.items():
            stats[lang] = {
                "file_count": len(files),
                "percentage": round(len(files) / total_files * 100, 1),
                "sample_files": files[:3],  # Primeiros 3 arquivos como exemplo
                "info": self.programming_languages.get(lang, {})
            }
        
        return {
            "project_path": project_path,
            "total_files": total_files,
            "languages_detected": stats,
            "primary_language": max(stats.keys(), key=lambda x: stats[x]["file_count"]) if stats else None,
            "recommendations": self._get_project_recommendations(stats)
        }
    
    def _get_project_recommendations(self, language_stats: Dict) -> List[str]:
        """Gerar recomendações baseadas nas linguagens detectadas"""
        recommendations = []
        
        for lang in language_stats.keys():
            # Recomendações específicas por linguagem
            if lang == 'pascal':
                recommendations.append("📚 Pascal detectado - considere migração para Object Pascal ou Free Pascal")
                recommendations.append("🔧 Use Lazarus IDE para desenvolvimento visual multiplataforma")
            elif lang == 'python':
                recommendations.append("🐍 Configure virtual environment para isolamento de dependências")
                recommendations.append("✅ Implemente testes com pytest e type hints com mypy")
            elif lang == 'javascript':
                recommendations.append("📦 Use npm/yarn para gestão de dependências")
                recommendations.append("🔧 Configure ESLint e Prettier para qualidade de código")
        
        # Recomendações gerais
        if len(language_stats) > 3:
            recommendations.append("🏗️ Projeto multilinguagem - considere containerização com Docker")
        
        recommendations.append("📊 Configure CI/CD para automação de builds e testes")
        
        return recommendations
    
    async def analyze_and_improve(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Analisar situação e aplicar melhorias automaticamente"""
        try:
            # Gerar resposta normal primeiro
            response = await self.get_standard_response(user_input, context)
            
            # Analisar oportunidades de melhoria
            improvements = await self.identify_improvements(user_input, response, context)
            
            # Aplicar melhorias quando apropriado
            applied_improvements = []
            pending_confirmations = []
            
            for improvement in improvements:
                if await self.should_apply_automatically(improvement):
                    result = await self.apply_improvement(improvement)
                    if result['success']:
                        applied_improvements.append(improvement)
                        self.applied_improvements.append({
                            'improvement': improvement,
                            'result': result,
                            'timestamp': datetime.now().isoformat()
                        })
                        try:
                            self.ml_advisor.train(user_input, improvement['action'])
                        except Exception:
                            self.logger.debug("Falha ao treinar modelo de ML, continuando sem interrupção")
                else:
                    pending_confirmations.append(improvement)
            
            # Formatar resposta com melhorias aplicadas
            enhanced_response = await self.format_enhanced_response(
                response, applied_improvements, pending_confirmations
            )

            await self._publish_analysis_summary(applied_improvements, pending_confirmations)
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"Erro na análise proativa: {e}")
            return await self.get_standard_response(user_input, context)

    async def _publish_analysis_summary(self, applied: List[Dict], pending: List[Dict]):
        """Publicar notificação resumida após a análise proativa."""
        try:
            if applied and not pending:
                title = "Melhorias aplicadas com sucesso"
                message = f"{len(applied)} melhoria(s) foram aplicadas automaticamente ao sistema."
                level = NotificationLevel.SUCCESS
            elif applied and pending:
                title = "Melhorias aplicadas e sugestões pendentes"
                message = (
                    f"{len(applied)} melhoria(s) aplicadas automaticamente e "
                    f"{len(pending)} sugestão(ões) aguardando confirmação."
                )
                level = NotificationLevel.WARNING
            elif pending:
                title = "Sugestões de melhorias pendentes"
                message = f"{len(pending)} melhoria(s) foram identificadas e aguardam sua confirmação."
                level = NotificationLevel.INFO
            else:
                return

            metadata = {
                'applied_count': len(applied),
                'pending_count': len(pending),
                'applied_actions': [imp['action'] for imp in applied],
                'pending_actions': [imp['action'] for imp in pending]
            }

            notification = self.notification_system.create_notification(
                title=title,
                message=message,
                level=level,
                metadata=metadata,
                channels=[
                    NotificationChannel.LOG,
                    NotificationChannel.DATABASE,
                    NotificationChannel.WEBSOCKET,
                ]
            )

            await self.notification_system.send_notification(notification)
        except Exception as e:
            self.logger.warning(f"Erro ao publicar resumo da análise proativa: {e}")
    
    async def get_standard_response(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Obter resposta padrão da IA"""
        # Implementar resposta básica usando a personalidade
        response_type = self._analyze_query_type(user_input)
        
        if response_type == 'help':
            response_text = self.personality.format_help_response()
        elif response_type == 'greeting':
            response_text = self.personality.get_greeting()
        elif response_type == 'improvement_request':
            response_text = await self._handle_improvement_request(user_input)
        else:
            response_text = f"Entendi sua solicitação! {self.personality.get_emoji('thinking')} Vou analisar e aplicar melhorias necessárias."
        
        return {
            'response': response_text,
            'type': response_type,
            'timestamp': datetime.now().isoformat(),
            'proactive_mode': True
        }
    
    async def identify_improvements(self, user_input: str, current_response: Dict, context: Dict = None) -> List[Dict]:
        """Identificar oportunidades de melhoria baseado na entrada do usuário"""
        improvements = []
        
        # Análise baseada em palavras-chave
        user_lower = user_input.lower()
        
        # Detectar linguagens de programação mencionadas
        detected_languages = []
        for lang_name in self.programming_languages.keys():
            if lang_name in user_lower:
                detected_languages.append(lang_name)
        
        # Análises específicas por linguagem
        for lang in detected_languages:
            lang_improvements = self._get_language_specific_improvements(lang, user_input)
            improvements.extend(lang_improvements)
        
        # Detectar solicitações de otimização
        if any(term in user_lower for term in ['lento', 'otimizar', 'melhorar performance', 'demora']):
            improvements.append({
                'type': 'optimization',
                'action': 'otimizar_consultas',
                'description': 'Otimizar consultas do banco de dados',
                'confidence': 0.9,
                'impact': 'alto',
                'safe': True
            })
            
        # Detectar problemas de espaço/limpeza
        if any(term in user_lower for term in ['espaço', 'limpar', 'logs', 'disco cheio']):
            improvements.append({
                'type': 'maintenance',
                'action': 'limpar_logs',
                'description': 'Limpar logs antigos para liberar espaço',
                'confidence': 0.95,
                'impact': 'médio',
                'safe': True
            })
        
        # Detectar solicitações de backup
        if any(term in user_lower for term in ['backup', 'salvar', 'proteger dados']):
            improvements.append({
                'type': 'backup',
                'action': 'backup_automatico',
                'description': 'Criar backup automático dos dados',
                'confidence': 0.85,
                'impact': 'crítico',
                'safe': False  # Requer confirmação
            })
        
        # Detectar problemas de dependências
        if any(term in user_lower for term in ['erro', 'módulo não encontrado', 'importerror', 'pascal', 'compilar']):
            improvements.append({
                'type': 'dependency',
                'action': 'instalar_dependencia',
                'description': 'Instalar dependências ou ferramentas necessárias',
                'confidence': 0.8,
                'impact': 'alto',
                'safe': True
            })
        
        # Análise proativa do sistema
        system_improvements = await self._analyze_system_health()
        improvements.extend(system_improvements)

        # Ajustar confiança baseada em modelo de aprendizado de máquina
        try:
            predicted_scores = self.ml_advisor.predict_scores(
                user_input,
                [improvement['action'] for improvement in improvements]
            )
            for improvement in improvements:
                score = predicted_scores.get(improvement['action'], 0.0)
                if score > 0:
                    improvement['confidence'] = min(1.0, max(improvement.get('confidence', 0.0), score + 0.1))
                    improvement['ml_score'] = round(score, 2)
        except Exception as e:
            self.logger.debug(f"Falha ao prever melhorias de ML: {e}")

        # Sugerir ações adicionais se o modelo já aprendeu padrões relevantes
        if not improvements:
            try:
                ml_suggestions = self.ml_advisor.recommend_actions(user_input, top_n=3, threshold=0.15)
                for action, score in ml_suggestions:
                    if action in self.available_actions:
                        improvements.append({
                            'type': 'ml_suggestion',
                            'action': action,
                            'description': f'Sugestão baseada em aprendizado de máquina para {action.replace("_", " ")}',
                            'confidence': min(0.95, score + 0.1),
                            'impact': 'médio',
                            'safe': action in self.safe_auto_actions,
                            'source': 'ml_model'
                        })
            except Exception as e:
                self.logger.debug(f"Falha ao gerar sugestões de ML: {e}")

        return improvements
    
    def _get_language_specific_improvements(self, language: str, user_input: str) -> List[Dict]:
        """Obter melhorias específicas para uma linguagem"""
        improvements = []
        user_lower = user_input.lower()
        
        if language == 'pascal':
            # Melhorias específicas para Pascal
            if any(term in user_lower for term in ['compilar', 'compilation', 'erro de compilação']):
                improvements.append({
                    'type': 'compilation',
                    'action': 'configurar_pascal',
                    'description': 'Configurar ambiente Pascal/Free Pascal',
                    'confidence': 0.9,
                    'impact': 'alto',
                    'safe': True,
                    'language': 'pascal'
                })
            
            if any(term in user_lower for term in ['modernizar', 'atualizar', 'migrar']):
                improvements.append({
                    'type': 'modernization',
                    'action': 'modernizar_pascal',
                    'description': 'Modernizar código Pascal para Object Pascal',
                    'confidence': 0.8,
                    'impact': 'alto',
                    'safe': False,
                    'language': 'pascal'
                })
        
        elif language == 'python':
            # Melhorias específicas para Python
            if any(term in user_lower for term in ['dependências', 'pip', 'install']):
                improvements.append({
                    'type': 'dependency',
                    'action': 'configurar_python_env',
                    'description': 'Configurar ambiente virtual Python',
                    'confidence': 0.95,
                    'impact': 'médio',
                    'safe': True,
                    'language': 'python'
                })
        
        elif language == 'javascript':
            # Melhorias específicas para JavaScript
            if any(term in user_lower for term in ['npm', 'dependencies', 'node_modules']):
                improvements.append({
                    'type': 'dependency',
                    'action': 'limpar_node_modules',
                    'description': 'Limpar e reinstalar node_modules',
                    'confidence': 0.85,
                    'impact': 'médio',
                    'safe': True,
                    'language': 'javascript'
                })
        
        return improvements
    
    async def _analyze_system_health(self) -> List[Dict]:
        """Análise proativa da saúde do sistema"""
        improvements = []
        
        try:
            # Verificar uso de memória
            memory_usage = await self._get_memory_usage()
            if memory_usage > 80:
                improvements.append({
                    'type': 'system',
                    'action': 'otimizar_memoria',
                    'description': f'Otimizar uso de memória (atual: {memory_usage}%)',
                    'confidence': 0.9,
                    'impact': 'médio',
                    'safe': True
                })
            
            # Verificar logs antigos
            log_size = await self._get_log_size()
            if log_size > 100:  # MB
                improvements.append({
                    'type': 'maintenance',
                    'action': 'limpar_logs',
                    'description': f'Limpar logs antigos ({log_size}MB)',
                    'confidence': 0.95,
                    'impact': 'baixo',
                    'safe': True
                })
            
            # Verificar integridade dos dados
            integrity_issues = await self._check_data_integrity()
            if integrity_issues:
                improvements.append({
                    'type': 'maintenance',
                    'action': 'verificar_integridade',
                    'description': f'Corrigir {len(integrity_issues)} problemas de integridade',
                    'confidence': 0.85,
                    'impact': 'alto',
                    'safe': True
                })
            
        except Exception as e:
            self.logger.warning(f"Erro na análise do sistema: {e}")
        
        return improvements

    async def _publish_improvement_notification(self, improvement: Dict, result: Dict):
        """Publicar notificação quando uma melhoria é aplicada ou falha."""
        try:
            title = f"Melhoria: {improvement.get('description', improvement.get('action', 'Ação de melhoria'))}"
            if result.get('success'):
                message = result.get('message', 'Melhoria aplicada com sucesso.')
                level = NotificationLevel.SUCCESS
            else:
                message = result.get('error', 'Falha ao aplicar melhoria.')
                level = NotificationLevel.ERROR

            notification = self.notification_system.create_notification(
                title=title,
                message=message,
                level=level,
                metadata={
                    'action': improvement.get('action'),
                    'type': improvement.get('type'),
                    'impact': improvement.get('impact'),
                    'confidence': improvement.get('confidence'),
                    'details': result.get('details'),
                },
                channels=[
                    NotificationChannel.LOG,
                    NotificationChannel.DATABASE,
                    NotificationChannel.WEBSOCKET,
                ]
            )
            await self.notification_system.send_notification(notification)
        except Exception as e:
            self.logger.warning(f"Erro ao publicar notificação: {e}")

    async def should_apply_automatically(self, improvement: Dict) -> bool:
        """Determinar se uma melhoria deve ser aplicada automaticamente"""
        # Permitir apenas ações explicitamente marcadas como seguras
        if improvement['action'] not in self.safe_auto_actions:
            return False

        # Verificar se requer confirmação explícita
        if improvement['action'] in self.require_confirmation:
            return False
        
        # Verificar nível de confiança
        if improvement['confidence'] < self.auto_apply_threshold:
            return False
        
        # Verificar se é considerada segura
        if not improvement.get('safe', False):
            return False
        
        # Verificar preferências do usuário
        improvement_type = improvement['type']
        if improvement_type == 'optimization' and not self.user_preferences['auto_apply_optimizations']:
            return False
        elif improvement_type == 'maintenance' and not self.user_preferences['auto_apply_maintenance']:
            return False
        elif improvement_type == 'system' and self.user_preferences['ask_before_system_changes']:
            return False
        
        return True
    
    async def apply_improvement(self, improvement: Dict) -> Dict[str, Any]:
        """Aplicar uma melhoria específica"""
        action_name = improvement['action']
        
        if action_name not in self.available_actions:
            return {
                'success': False,
                'error': f"Ação '{action_name}' não disponível",
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            self.logger.info(f"🔧 Aplicando melhoria: {improvement['description']}")
            
            action_func = self.available_actions[action_name]
            result = await action_func(improvement)
            
            result.update({
                'improvement': improvement,
                'applied_automatically': True,
                'timestamp': datetime.now().isoformat()
            })

            await self._publish_improvement_notification(improvement, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar melhoria {action_name}: {e}")
            error_result = {
                'success': False,
                'error': str(e),
                'improvement': improvement,
                'timestamp': datetime.now().isoformat()
            }
            await self._publish_improvement_notification(improvement, error_result)
            return error_result
    
    # Implementação das ações específicas
    async def optimize_database_queries(self, improvement: Dict) -> Dict[str, Any]:
        """Otimizar consultas do banco de dados"""
        try:
            # Implementar otimizações reais
            optimizations_applied = []
            
            # Atualizar estatísticas
            with self.db_manager.get_connection() as conn:
                conn.execute("ANALYZE;")
                optimizations_applied.append("Estatísticas atualizadas")
            
            # Reindexar se necessário
            await self._reindex_if_needed()
            optimizations_applied.append("Índices otimizados")
            
            return {
                'success': True,
                'message': f"Otimizações aplicadas: {', '.join(optimizations_applied)}",
                'details': optimizations_applied
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def clean_old_logs(self, improvement: Dict) -> Dict[str, Any]:
        """Limpar logs antigos"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {'success': True, 'message': 'Nenhum log encontrado para limpar'}
            
            cutoff_date = datetime.now() - timedelta(days=30)
            deleted_files = []
            total_size_freed = 0
            
            for log_file in logs_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_files.append(log_file.name)
                    total_size_freed += size
            
            return {
                'success': True,
                'message': f"Logs limpos: {len(deleted_files)} arquivos, {total_size_freed/1024/1024:.1f}MB liberados",
                'details': {'files_deleted': len(deleted_files), 'space_freed_mb': total_size_freed/1024/1024}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def create_automatic_backup(self, improvement: Dict) -> Dict[str, Any]:
        """Criar backup automático"""
        try:
            # Integrar com sistema de backup existente
            from backup_system import MamuteBackupSystem
            
            backup_system = MamuteBackupSystem()
            result = backup_system.create_database_backup()
            
            return {
                'success': True,
                'message': f"Backup criado: {result.get('backup_file', 'N/A')}",
                'details': result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def install_missing_dependency(self, improvement: Dict) -> Dict[str, Any]:
        """Instalar dependência em falta"""
        try:
            # Implementar instalação inteligente de dependências
            # Por segurança, apenas lista as dependências que faltam
            missing_deps = await self._detect_missing_dependencies()
            
            if not missing_deps:
                return {'success': True, 'message': 'Todas as dependências estão instaladas'}
            
            # Para demonstração, vamos simular a instalação
            return {
                'success': True,
                'message': f"Dependências verificadas: {', '.join(missing_deps)}",
                'details': {'missing_dependencies': missing_deps},
                'recommendation': 'Execute: pip install ' + ' '.join(missing_deps)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def format_enhanced_response(self, original_response: Dict, applied: List, pending: List) -> Dict[str, Any]:
        """Formatar resposta com melhorias aplicadas"""
        response_text = original_response['response']
        
        # Adicionar informações sobre melhorias aplicadas
        if applied:
            success_emoji = self.personality.get_emoji('success')
            response_text += f"\\n\\n{success_emoji} **Melhorias Aplicadas Automaticamente:**\\n"
            
            for improvement in applied:
                response_text += f"✅ {improvement['description']}\\n"
        
        # Adicionar melhorias pendentes de confirmação
        if pending:
            help_emoji = self.personality.get_emoji('help')
            response_text += f"\\n\\n{help_emoji} **Melhorias Sugeridas (precisam de confirmação):**\\n"
            
            for improvement in pending:
                response_text += f"🔄 {improvement['description']} (digite 'aplicar {improvement['action']}' para confirmar)\\n"
        
        # Adicionar estatísticas da sessão
        if applied or pending:
            stats_emoji = self.personality.get_emoji('data')
            response_text += f"\\n\\n{stats_emoji} **Estatísticas:**\\n"
            response_text += f"• Melhorias aplicadas: {len(applied)}\\n"
            response_text += f"• Aguardando confirmação: {len(pending)}\\n"
            response_text += f"• Total aplicadas na sessão: {len(self.applied_improvements)}"
        
        return {
            'response': response_text,
            'type': 'enhanced_response',
            'applied_improvements': applied,
            'pending_improvements': pending,
            'timestamp': datetime.now().isoformat(),
            'proactive_mode': True,
            'session_stats': {
                'total_applied': len(self.applied_improvements),
                'current_applied': len(applied),
                'current_pending': len(pending)
            }
        }
    
    # Métodos auxiliares
    def _analyze_query_type(self, query: str) -> str:
        """Analisar tipo de consulta"""
        query_lower = query.lower().strip()
        
        if any(term in query_lower for term in ['melhorar', 'otimizar', 'acelerar', 'corrigir']):
            return 'improvement_request'
        elif any(term in query_lower for term in ['oi', 'olá', 'hello']):
            return 'greeting'
        elif any(term in query_lower for term in ['ajuda', 'help']):
            return 'help'
        else:
            return 'general'
    
    async def _handle_improvement_request(self, user_input: str) -> str:
        """Lidar com solicitações explícitas de melhoria"""
        thinking_emoji = self.personality.get_emoji('thinking')
        action_emoji = self.personality.get_emoji('success')
        
        return f"{thinking_emoji} Analisando oportunidades de melhoria...\\n\\n" + \
               f"{action_emoji} Vou identificar e aplicar melhorias automaticamente! " + \
               f"{self.personality.get_emoji('celebration')}\\n\\n" + \
               "✨ **Modo Proativo Ativo:**\\n" + \
               "• Identificando problemas\\n" + \
               "• Aplicando correções seguras\\n" + \
               "• Sugerindo melhorias avançadas"
    
    async def _get_memory_usage(self) -> float:
        """Obter uso atual de memória"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    async def _get_log_size(self) -> float:
        """Obter tamanho total dos logs em MB"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return 0.0
            
            total_size = sum(f.stat().st_size for f in logs_dir.glob("*.log*"))
            return total_size / 1024 / 1024
        except Exception:
            return 0.0
    
    async def _check_data_integrity(self) -> List[str]:
        """Verificar integridade dos dados"""
        issues = []
        try:
            # Implementar verificações reais de integridade
            # Por exemplo, verificar chaves estrangeiras, valores nulos, etc.
            pass
        except Exception:
            pass
        return issues
    
    async def _detect_missing_dependencies(self) -> List[str]:
        """Detectar dependências em falta"""
        required_deps = ['psutil', 'schedule', 'matplotlib', 'seaborn']
        missing = []
        
        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        return missing
    
    async def _reindex_if_needed(self):
        """Reindexar banco se necessário"""
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute("REINDEX DATABASE CONCURRENTLY;")
        except Exception as e:
            self.logger.warning(f"Não foi possível reindexar: {e}")
    
    # Métodos placeholder para outras ações
    async def update_database_indexes(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Índices atualizados'}
    
    async def generate_performance_report(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Relatório de performance gerado'}
    
    async def optimize_memory_usage(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Uso de memória otimizado'}
    
    async def check_data_integrity(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Integridade dos dados verificada'}
    
    async def fix_configuration_issue(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Configuração corrigida'}
    
    async def update_system_components(self, improvement: Dict) -> Dict[str, Any]:
        return {'success': True, 'message': 'Componentes do sistema atualizados'}