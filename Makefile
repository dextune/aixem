.PHONY: build examples corpus hierarchical-corpus viewer-corpus validate authoring-check agent-evals agent-evals-2 agent-evals-3 check test render render-hierarchical screenshots route verify-053 verify-054 verify-055 verify-056 verify-057 audit-docs package clean

examples:
	python tools/docs/build_authoring_examples.py

build:
	python tools/docs/build_all.py

corpus:
	python tools/validate_symbol_corpus.py --all --repeat 3 --emit-report

hierarchical-corpus:
	python tools/validate_hierarchical_corpus.py --repeats 3

viewer-corpus:
	python tools/validate_reference_viewer_corpus.py --repeats 3 --screenshots

validate:
	python tools/docs/validate_docs.py

authoring-check:
	python tools/docs/authoring_validation.py

agent-evals:
	python tools/docs/run_agent_evals.py

agent-evals-2:
	python tools/run_agent_evals_2.py

check:
	python tools/docs/check_release.py

test:
	python tools/docs/run_tests.py

render:
	python implementation/schematic/render_project.py examples/electronics-grid-controller/project.aixproj.json

render-hierarchical:
	python implementation/schematic/render_project.py validation/corpus/hierarchical-project-1/cases/H001-two-sheet-power-+-control/project.aixproj.json

screenshots:
	python tools/docs/capture_site.py

route:
	python tools/docs/query_route.py "$(QUERY)"

verify-053:
	python tools/verify_release_053.py --all-passes

verify-054:
	python tools/verify_release_054.py --all-passes

verify-055:
	python tools/verify_release_055.py --all-passes

audit-docs:
	python tools/docs/audit_repository_docs.py --require-redirects

package:
	python tools/package_release_057.py

clean:
	python tools/docs/clean.py

agent-evals-3:
	python tools/run_agent_evals_3.py --tier-a-only

verify-056:
	python tools/verify_release_056.py --all-passes

verify-057:
	python tools/verify_release_057.py --all-passes
