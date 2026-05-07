### This is is specifically for the Deployment.yaml that let us understand more about how to write the deployment.yaml

So, everything starts from AKMS, which means:::
    A = apiVersion
    K = kind
    M = metadata
    S = spec


The S, spec on top contains RST which means::
    R = replicas
    S = selector
        - Under S, it have the .matchLabels which should be match with the {template.app}
    T = template
        - Under T, they have MAS::
            M = metadata
            A = app (**This should match with the spec.selector.matchLabels)
            S = spec