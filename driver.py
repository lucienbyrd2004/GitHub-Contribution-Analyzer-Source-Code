import git_parser

if __name__== "__main__":
    pushes = git_parser.get_commit_from_name("DebraBeat", 5)

    for p in pushes:
        print(p)

